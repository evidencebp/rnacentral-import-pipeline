process release_note {
  containerOptions "--contain --workdir $baseDir/work/tmp --bind $baseDir"

  publishDir "${params.ftp_export.publish}/", mode: 'move'
  when: params.ftp_export.release_note.run

  input:
  path(template_file) from Channel.fromPath('files/ftp-export/release_note.txt')

  output:
  path('release_notes.txt') into __notes

  """
  rnac ftp-export release-note ${template_file} ${params.release} release_notes.txt
  mkdir -p ${params.ftp_export.publish}/help-requests
  """
}

process md5 {
  publishDir "${params.ftp_export.publish}/md5/", mode: 'move'
  container ''

  when: params.ftp_export.md5.run

  input:
  path(query) from Channel.fromPath('files/ftp-export/md5/md5.sql')
  path('template.txt') from Channel.fromPath('files/ftp-export/md5/readme.txt')

  output:
  path("example.txt") into __md5_example
  path("md5.tsv.gz") into __md5_files
  path("readme.txt") into __md5_readme

  """
  psql -v ON_ERROR_STOP=1 -f "$query" "$PGDATABASE" > md5.tsv
  head -10 md5.tsv > example.txt
  gzip md5.tsv
  cat template.txt > readme.txt
  """
}

process id_mapping {
  publishDir "${params.ftp_export.publish}/id_mapping/", mode: 'copy'
  container ''

  when: params.ftp_export.id_mapping.run

  input:
  path(query) from Channel.fromPath('files/ftp-export/id-mapping/id_mapping.sql')
  path('template.txt') from Channel.fromPath('files/ftp-export/id-mapping/readme.txt')

  output:
  path('id_mapping.tsv.gz') into id_mapping
  path("example.txt") into __id_mapping_example
  path("readme.txt") into __id_mapping_readme

  """
  set -euo pipefail

  psql -v ON_ERROR_STOP=1 -f "$query" "$PGDATABASE" > raw_id_mapping.tsv
  rnac ftp-export id-mapping raw_id_mapping.tsv - | sort -u > id_mapping.tsv
  head id_mapping.tsv > example.txt
  gzip id_mapping.tsv
  cat template.txt > readme.txt
  """
}

process database_id_mapping {
  publishDir "${params.ftp_export.publish}/id_mapping/database_mappings/", mode: 'move'
  containerOptions "--contain --workdir $baseDir/work/tmp --bind $baseDir"

  when: params.ftp_export.id_mapping.by_database.run

  input:
  path('id_mapping.tsv.gz') from id_mapping

  output:
  path('*.tsv') into __database_mappings

  """
  set -euo pipefail

  zcat id_mapping.tsv.gz | awk '{ print >> (tolower(\$2) ".tsv") }'
  """
}

process rfam_annotations {
  publishDir "${params.ftp_export.publish}/rfam/", mode: 'move'
  when: params.ftp_export.rfam.annotations.run

  input:
  path(query) from Channel.fromPath('files/ftp-export/rfam/rfam-annotations.sql')
  path('template.txt') from Channel.fromPath('files/ftp-export/rfam/readme.txt')

  output:
  path('rfam_annotations.tsv.gz') into __rfam_files
  path("example.txt") into __rfam_example
  path("readme.txt") into __rfam_readme

  """
  set -o pipefail

  psql -v ON_ERROR_STOP=1 -f "$query" "$PGDATABASE" > rfam_annotations.tsv
  head rfam_annotations.tsv > example.txt
  gzip rfam_annotations.tsv
  cat template.txt > readme.txt
  """
}

process inactive_fasta {
  publishDir "${params.ftp_export.publish}/sequences/", mode: 'move'
  when: params.ftp_export.sequences.inactive.run

  input:
  path(query) from Channel.fromPath('files/ftp-export/sequences/inactive.sql')

  output:
  path('rnacentral_inactive.fasta.gz') into __sequences_inactive

  """
  set -euo pipefail

  export PYTHONIOENCODING=utf8
  psql -v ON_ERROR_STOP=1 -f "$query" "$PGDATABASE" | json2fasta.py - - | gzip > rnacentral_inactive.fasta.gz
  """
}

process active_fasta {
  publishDir "${params.ftp_export.publish}/sequences/", mode: 'copy'
  when: params.ftp_export.sequences.active.run

  input:
  path(query) from Channel.fromPath('files/ftp-export/sequences/active.sql')
  path('template.txt') from Channel.fromPath('files/ftp-export/sequences/readme.txt')

  output:
  path('rnacentral_active.fasta.gz') into active_sequences
  path('example.txt') into __sequences_example
  path('readme.txt') into __sequences_readme

  """
  set -euo pipefail

  export PYTHONIOENCODING=utf8
  psql -v ON_ERROR_STOP=1 -f "$query" "$PGDATABASE" | json2fasta.py - rnacentral_active.fasta
  head rnacentral_active.fasta > example.txt
  gzip rnacentral_active.fasta
  cat template.txt > readme.txt
  """
}

process species_specific_fasta {
  publishDir "${params.ftp_export.publish}/sequences/", mode: 'move'
  when: params.ftp_export.sequences.species.run

  input:
  path(query) from Channel.fromPath('files/ftp-export/sequences/species-specific.sql')

  output:
  path('rnacentral_species_specific_ids.fasta.gz') into __sequences_species

  """
  set -euo pipefail

  export PYTHONIOENCODING=utf8
  psql -v ON_ERROR_STOP=1 -f "$query" "$PGDATABASE" | json2fasta.py - - | gzip > rnacentral_species_specific_ids.fasta.gz
  """
}

process find_db_to_export {
  input:
  path(query) from Channel.fromPath('files/ftp-export/sequences/databases.sql')

  output:
  stdout into raw_dbs

  """
  psql -v ON_ERROR_STOP=1 -f "$query" "$PGDATABASE"
  """
}

raw_dbs
  .splitCsv()
  .combine(Channel.fromPath('files/ftp-export/sequences/database-specific.sql'))
  .set { db_sequences }

process database_specific_fasta {
  tag { db }
  maxForks params.ftp_export.sequences.by_database.max_forks
  publishDir "${params.ftp_export.publish}/sequences/by-database", mode: 'move'
  when: params.ftp_export.sequences.by_database.run

  input:
  set val(db), file(query) from db_sequences

  output:
  file('*.fasta') into __database_sequences_species

  script:
  """
  set -o pipefail

  export PYTHONIOENCODING=utf8
  psql -v ON_ERROR_STOP=1 -f "$query" -v db='%${db}%' "$PGDATABASE" > raw.json
  json2fasta.py raw.json ${db.toLowerCase().replaceAll(' ', '_')}.fasta
  """
}

active_sequences.into { nhmmer_valid; nhmmer_invalid }

process extract_nhmmer_valid {
  publishDir "${params.ftp_export.publish}/sequences/.internal/", mode: 'move'
  when: params.ftp_export.sequences.nhmmer.run

  input:
  file(rna) from nhmmer_valid

  output:
  path('rnacentral_nhmmer.fasta') into __sequences_nhmmer

  """
  set -euo pipefail

  export PYTHONIOENCODING=utf8
  zcat $rna | rnac ftp-export sequences valid-nhmmer - rnacentral_nhmmer.fasta
  """
}

process extract_nhmmer_invalid {
  publishDir "${params.ftp_export.publish}/sequences/.internal/", mode: 'move'
  when: params.ftp_export.sequences.nhmmer.run

  input:
  file(rna) from nhmmer_invalid

  output:
  path('rnacentral_nhmmer_excluded.fasta') into __sequences_invalid_nhmmer

  """
  set -euo pipefail

  export PYTHONIOENCODING=utf8
  zcat $rna | rnac ftp-export sequences invalid-nhmmer - rnacentral_nhmmer_excluded.fasta
  """
}

process find_ensembl_chunks {
  executor 'local'
  when: params.ftp_export.ensembl.run

  output:
  stdout raw_ensembl_ranges

  """
  rnac upi-ranges ${params.ftp_export.ensembl.chunk_size}
  """
}

raw_ensembl_ranges
  .splitCsv()
  .combine(Channel.fromPath('files/ftp-export/ensembl/ensembl-xrefs.sql'))
  .set { ensembl_ranges }

process ensembl_export_chunk {
  maxForks params.ftp_export.ensembl.maxForks

  input:
  set val(table), val(min), val(max), file(query) from ensembl_ranges

  output:
  set val(min), val(max), file('raw_xrefs.json') into raw_ensembl_chunks

  script:
  """
  psql -f $query --variable min=$min --variable max=$max "$PGDATABASE" > raw_xrefs.json
  """
}

raw_ensembl_chunks
  .combine(Channel.fromPath('files/ftp-export/ensembl/schema.json'))
  .set { ensembl_chunks }

process ensembl_process_chunk {
  publishDir "${params.ftp_export.publish}/json/", mode: 'move'

  input:
  tuple val(min), val(max), file(raw), file(schema) from ensembl_chunks

  output:
  file("ensembl-xref-$min-${max}.json") into __ensembl_export

  script:
  def result = "ensembl-xref-$min-${max}.json"
  """
  rnac ftp-export ensembl --schema=$schema $raw $result
  """
}

process rfam_go_matches {
  memory params.ftp_export.rfam.go_annotations.memory
  publishDir "${params.ftp_export.publish}/go_annotations/", mode: 'move'
  when: params.ftp_export.rfam.go_annotations.run

  input:
  path(query) from Channel.fromPath('files/ftp-export/go_annotations/rnacentral_rfam_annotations.sql')

  output:
  path("rnacentral_rfam_annotations.tsv.gz") into __go_annotations

  """
  psql -f "$query" "$PGDATABASE" > raw_go.json
  rnac ftp-export rfam-go-annotations raw_go.json rnacentral_rfam_annotations.tsv
  gzip rnacentral_rfam_annotations.tsv
  """
}

process find_genome_coordinate_jobs {
  when: params.ftp_export.coordinates.run

  input:
  path(query) from Channel.fromPath('files/ftp-export/genome_coordinates/known-coordinates.sql')

  output:
  file('coordinates.txt') into species_to_format

  """
  psql -v ON_ERROR_STOP=1 -f $query $PGDATABASE > coordinates.txt
  """
}

species_to_format
  .splitCsv()
  .combine(Channel.fromPath('files/ftp-export/genome_coordinates/query.sql'))
  .set { coordinates_to_fetch }

process coordinate_readme {
  publishDir "${params.ftp_export.publish}/genome_coordinates/", mode: 'copy'
  when: params.ftp_export.coordinates.run

  input:
  path(raw) from Channel.fromPath('files/ftp-export/genome_coordinates/readme.mkd')

  output:
  file('readme.txt') into __coordinate_readmes

  """
  cat $raw > readme.txt
  """
}

process fetch_raw_coordinate_data {
  tag { "${assembly}-${species}" }
  maxForks params.ftp_export.coordinates.maxForks

  input:
  tuple val(assembly), val(species), val(taxid), file(query) from coordinates_to_fetch

  output:
  tuple val(assembly), val(species), file('result.json') into raw_coordinates optional true

  """
  psql -v ON_ERROR_STOP=1 -v "assembly_id=$assembly" -f $query "$PGDATABASE" > result.json
  if [[ -z result.json ]]; then
    rm result.json
  fi
  """
}

raw_coordinates
  .filter { result -> !result.isEmpty() }
  .into { bed_coordinates; gff_coordinates }

process format_bed_coordinates {
  tag { "${assembly}-${species}" }
  publishDir "${params.ftp_export.publish}/genome_coordinates/bed/", mode: 'copy'
  when: params.ftp_export.coordinates.bed.run

  input:
  set val(assembly), val(species), file(raw_data) from bed_coordinates

  output:
  set val(assembly), file("${species}.${assembly}.bed.gz") into bed_files

  script:
  """
  set -euo pipefail

  rnac ftp-export coordinates as-bed $raw_data |\
  sort -k1,1 -k2,2n |\
  gzip > ${species}.${assembly}.bed.gz
  """
}

// process generate_big_bed {
//   publishDir "${params.ftp_export.publish}/genome_coordinates/bed", mode: 'copy'

//   input:
//   set val assembly, path(bed_file) from bed_files

//   output:
//   file(bigBed) into big_bed_files

//   script:
//   chrom = "${bed_file.baseName}.chrom.sizes"
//   bigBed = "${bed_file.baseName}.bigBed"
//   """
//   fetchChromSizes "$assembly" > "$chrom"
//   bedToBigBed -type -type=bed12+3 bed_file $chrom > $bigBed
//   """
// }

process generate_gff3 {
  tag { "${assembly}-${species}" }
  memory params.ftp_export.coordinates.gff3.memory
  publishDir "${params.ftp_export.publish}/genome_coordinates/gff3", mode: 'move'
  when: params.ftp_export.coordinates.gff3.run

  input:
  tuple val(assembly), val(species), file(raw_data) from gff_coordinates

  output:
  file("${species}.${assembly}.gff3.gz") into gff3_files

  script:
  """
  set -euo pipefail

  rnac ftp-export coordinates as-gff3 $raw_data - | gzip > ${species}.${assembly}.gff3.gz
  """
}
