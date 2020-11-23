process fetch_single_files {
  when { params.databases.ena.run }

  output:
  path("**/*.ncr")

  script:
  def remote = params.databases.ena.remote
  """
  rsync \
    -avPL \
    --prune-empty-dirs \
    --include='*/' \
    --include='**/*.ncr.gz' \
    --exclude='*.fasta.gz' \
    "$remote/con-std_latest/" con-std

  rsync \
    -avPL \
    --prune-empty-dirs \
    --include='*/' \
    --include='**/*.ncr.gz' \
    --exclude='*.fasta.gz' \
    "$remote/tls/public/" tls

  rsync \
    -avPL \
    --prune-empty-dirs \
    --include='*/' \
    --include='**/*.ncr.gz' \
    --exclude='*.fasta.gz' \
    "$remote/tsa/public/" tsa
  """
}

process find_wgs_directories {
  when { params.databases.ena.run }

  output:
  path('paths')

  script:
  def remote = params.databases.ena.remote
  """
  find $remote/wgs/public -mindepth 1 -maxdepth 1 > paths
  """
}

process fetch_wgs_directories {
  input:
  path(to_fetch)

  output:
  path('files/*.ncr')

  script:
  """
  rsync \
    -avPL \
    --prune-empty-dirs \
    --include='**/*.ncr.gz' \
    --exclude='*.fasta.gz' \
    "$to_fetch" raw

  mkdir files
  mkdir chunks
  find raw -type f > ids
  split -n l/4000 ids chunks/chunk-
  find chunks/ -type f | xargs -I {} paste -sd ' ' {} | xargs -I {} sh -c 'zcat {} > "$(mktemp -p files chunk-XXXXX.ncr)"'
  """
}

process fetch_tpa {
  when { params.databases.ena.run }

  input:
  path(urls)

  output:
  path('tpa.tsv')

  """
  cat $urls | xargs -I {} wget -O - {} >> tpa.tsv
  """
}

process process_file {
  tag { "$raw" }

  input:
  tuple path(raw), path(tpa)

  output:
  path('*.csv')

  """
  zcat $raw > sequences.dat
  ena2fasta.py sequences.dat sequences.fasta
  ribotyper.pl sequences.fasta ribotyper-results
  rnac ena parse sequences.dat $tpa ribotyper-results
  """
}

workflow ena {
  emit: data
  main:
    Channel.fromPath('files/import-data/ena/tpa-urls.txt') | fetch_tpa | set { tpa }

    find_wgs_directories | fetch_wgs_directories | set { wgs_files }

    fetch_single_files \
    | mix(wgs_files)
    | flatten \
    | combine(tpa) \
    | process_file \
    | set { processed_wgs }
}
