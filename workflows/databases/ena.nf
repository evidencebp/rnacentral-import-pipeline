process fetch_single_files {
  when { params.databases.ena.run }

  output:
  path("**/*.ncr.gz")

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

  find . -type f -empty -delete
  find . -type f | xargs -I {} gzip --quiet -l {} | awk '{ if (\$2 == 0) print \$4 }' | xargs -I {} rm {}.gz

  find . -type f |\
  xargs -I {} zgrep -Hc '^ID' {} |\
  awk -F ':' '{ if (\$2 > 100000) print \$1 }' > too-large

  mkdir large-splits
  xargs -a too-large -I {} split-sequences --max-sequences 20000 --format-name='ncr' --remove-file {} large-splits
  find large-splits -type f | xargs -I {} gzip {}
  """
}

process find_wgs_directories {
  when { params.databases.ena.run }

  output:
  path('paths')

  script:
  def remote = params.databases.ena.remote
  """
  find $remote/wgs/public -mindepth 1 -maxdepth 1 -not -empty > paths
  """
}

process fetch_wgs_directories {
  tag { "${file(to_fetch).name}" }

  input:
  val(to_fetch)

  output:
  path('files/*')

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
  split -n l/30 ids chunks/chunk-
  find chunks -type f -empty -delete
  find chunks/ -type f | xargs -I {} group-wgs {} "${file(to_fetch).name}" files
  """
}

process fetch_metadata {
  when { params.databases.ena.run }

  input:
  path(urls)

  output:
  tuple path('tpa.tsv'), path('model-lengths.csv')

  """
  cat $urls | xargs -I {} wget -O - {} >> tpa.tsv
  cmstat \$RIBODIR/models/ribo.0p20.extra.cm | grep -v '^#' | awk '{ printf("%s,%d\\n", \$2, \$6); }' > model-lengths.csv
  """
}

process process_file {
  memory '4GB'
  tag { "$raw" }

  input:
  tuple path(raw), path(tpa), path(model_lengths)

  output:
  path('*.csv')

  """
  zcat $raw > sequences.dat
  ena2fasta.py sequences.dat sequences.fasta
  /rna/ribovore/ribotyper.pl sequences.fasta ribotyper-results
  rnac ena parse --counts $raw-counts.txt sequences.dat $tpa ribotyper-results $model_lengths .

  if [[ -e $baseDir/ena-counts/$raw-counts.txt ]]; then
    echo 1>&2 "Failed to copy counts into final directory"
    exit 1
  fi
  cp $raw-counts.txt $baseDir/ena-counts
  """
}

workflow ena {
  emit: data
  main:
    Channel.fromPath('files/import-data/ena/tpa-urls.txt') | set { urls }

    find_wgs_directories \
    | splitCsv \
    | map { row -> row[0] } \
    | fetch_wgs_directories \
    | set { wgs_files }

    fetch_single_files \
    | mix(wgs_files) \
    | flatten \
    | combine(fetch_metadata(urls)) \
    | process_file \
    | set { data }
}
