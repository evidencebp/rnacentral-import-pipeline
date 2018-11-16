#!/usr/bin/env nextflow

process species_to_map {
  executor 'local'

  input:
  file(query) from Channel.fromPath('files/genome-mapping/mappable.sql')

  output:
  stdout into raw_genomes

  """
  psql -v ON_ERROR_STOP=1 -f "$query" "$PGDATABASE"
  """
}

raw_genomes
  .splitCsv()
  .into { assemblies; genomes_to_fetch }

assemblies
  .combine(Channel.fromPath('files/genome-mapping/find-unmapped.sql'))
  .view()
  .set { assemblies_to_fetch }

process fetch_unmapped_sequences {
  tag { species }
  scratch true

  input:
  set val(species), val(assembly_id), val(taxid), val(division), file(query) from assemblies_to_fetch

  output:
  set species, file('parts/*.fasta') into split_sequences

  script:
  """
  sql2fasta -v taxid=$taxid -v assembly_id=$assembly_id $query ${params.qa.rfam_scan.chunk_size}
  """
}

process download_genome {
  tag { species }
  scratch true

  input:
  set val(species), val(assembly), val(taxid), val(division) from genomes_to_fetch

  output:
  set val(species), file('*.fa'), file('11.ooc') into genomes

  script:
  def engine = new groovy.text.SimpleTemplateEngine()
  def url = engine
    .createTemplate(params.genome_mapping.sources[division])
    .make([species: species])
    .toString()
  """
  fetch genome '$url' ${species}.fasta

  blat \
    -makeOoc=11.ooc \
    -stepSize=${params.genome_mapping.blat_options.step_size} \
    -repMatch=${params.genome_mapping.blat_options.rep_match} \
    -minScore=${params.genome_mapping.blat_options.min_score} \
    ${species}.fasta /dev/null /dev/null
  """
}

genomes
  .join(split_sequences)
  .flatMap { species, chrs, ooc_file, chunks ->
    [chrs, chunks].combinations().inject([]) { acc, it -> acc << [species, ooc_file] + it }
  }
  .set { targets }

process blat {
  input:
  set val(species), file(ooc), file(chromosome), file(chunk) from targets

  output:
  set file(species), file('output.psl') into blat_results

  """
  blat \
    -ooc=$ooc \
    -noHead \
    -q=rna \
    -stepSize=${params.genome_mapping.blat_options.step_size} \
    -repMatch=${params.genome_mapping.blat_options.rep_match} \
    -minScore=${params.genome_mapping.blat_options.min_score} \
    -minIdentity=${params.genome_mapping.blat_options.min_identity} \
    $chromosome $chunk output.psl
  """
}

 blat_results
  .groupTuple()
  .map { it -> it[1] }
  .set { species_results }

process select_mapped_locations {
  memory '10 GB'

  input:
  file('*.psl') from species_results

  output:
  file 'locations.csv' into selected_locations

  """
  set -o pipefail

  sort -t 10 *.psl | rnac genome-mapping select-hits - locations.csv
  """
}

process load_genome_mapping {
  maxForks 1

  input:
  file('raw*.csv') from selected_locations.collect()
  file(ctl) from Channel.fromPath('files/genome-mapping/load.ctl')

  output:
  val('done') into mapped_genomes

  script:
  """
  split-and-load $ctl 'raw*.csv' ${params.import_data.chunk_size} genome-mapping
  """
}
