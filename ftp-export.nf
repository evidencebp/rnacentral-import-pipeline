process release_note {
  publishDir "${params.ftp_export.publish}/", mode: 'copy'

  input:
  file template_file from Channel.fromPath('files/ftp-export/release_note.txt')

  output:
  file 'release_notes.txt' into __notes

  """
  rnac ftp-export release-note ${template_file} ${params.release} release_notes.txt
  """
}

process md5 {
  publishDir "${params.ftp_export.publish}/md5/", mode: 'copy'

  input:
  file query from Channel.fromPath('files/ftp-export/md5/md5.sql')
  file 'readme.txt' form Channel.fromPath('files/ftp-export/md5/readme.txt')

  output:
  file "example.txt" into __md5_files
  file "md5.tsv.gz" into __md5_files
  file "readme.txt" into __md5_files

  """
  psql -f "$query" "$PGDATABASE" > md5.tsv
  head -10 md5.tsv > example.tsv
  gzip md5.tsv
  """
}

process id_mapping {
  publishDir "${params.ftp_export.publish}/id_maping/", mode: 'copy'

  input:
  file query from Channel.fromPath('files/ftp-export/id-mapping/id_mapping.sql')
  file 'readme.txt' from Channel.fromPath('files/ftp-export/id-mapping/readme.txt')

  output:
  file 'id_mapping.tsv.gz' into id_mapping
  file "example.txt" into __id_mapping_files
  file "readme.txt" into __id_mapping_files

  """
  psql -f "$query" "$PGDATABASE" > raw_id_mapping.tsv
  rnac ftp-export id-mapping raw_id_mapping.tsv id_mapping.tsv
  head id_mapping.tsv > example.tsv
  gzip id_mapping.tsv
  """
}

process database_id_mapping {
  publishDir "${params.ftp_export.publish}/id_maping/database_mappings/", mode: 'copy'

  input:
  file 'id_mapping.tsv.gz' into id_mapping

  output:
  file '*.tsv' into __database_mappings

  """
  zcat id_mapping.tsv.gz | awk '{ print >> (tolower($2) ".tsv") }'
  """
}

process rfam_annotations {
  publishDir "${params.ftp_export.publish}/rfam/", mode: 'copy'

  input:
  file query from Channel.from('files/ftp-export/rfam/rfam-annotations.sql')

  output:
  file 'rfam_annotations.tsv.gz' into __rfam_files
  file "example.txt" into __rfam_files
  file "readme.txt" into __rfam_files

  """
  psql -f "$query" "$PGDATABASE" | gzip > rfam_annotations.tsv.gz
  zcat rfam_annotations.tsv.gz | head > example.txt
  """
}

process inactive_fasta {
  publishDir "${params.ftp_export.publish}/sequences/", mode: 'copy'

  input:
  file query from Channel.fromPath('files/ftp-export/sequences/inactive.sql')

  output:
  file 'rnacentral_inactive.fasta.gz' into __sequences

  """
  psql -f "$query" "$PGDATABASE" | json2fasta.py - - | gzip > rnacentral_inactive.fasta.gz
  """
}

process active_fasta {
  publishDir "${params.ftp_export.publish}/sequences/", mode: 'copy'

  input:
  file query from Channel.fromPath('files/ftp-export/sequences/active.sql')

  output:
  file 'rnacentral_active.fasta.gz' into active_sequences
  file 'example.txt' into __sequences
  file 'readme.txt' into __sequences

  """
  psql -f "$query" "$PGDATABASE" | json2fasta.py - rnacentral_active.fasta
  head rnacentral_active.fasta > example.txt
  gzip rnacentral_active.fasta
  """

}

process species_specific_fasta {
  publishDir "${params.ftp_export.publish}/sequences/", mode: 'copy'

  input:
  file query from Channel.fromPath('files/ftp-export/sequences/species-specific.sql')

  output:
  file 'rnacentral_species_specific_ids.fasta.gz' into __sequences

  """
  psql -f "$query" "$PGDATABASE" | json2fasta.py - - | gzip > rnacentral_active.fasta.gz
  """
}

process nhmmer_fasta {
  publishDir "${params.ftp_export.publish}/sequences/.internal/", mode: 'copy'

  input:
  file 'rnacentral_active.fasta.gz' from active_sequences

  output:
  file 'rnacentral_nhmmer*.fasta' into __sequences

  """
  zcat rnacentral_active.fasta.gz | rnac ftp-export sequences split-for-nhmmer -
  """
}

process find_ensembl_chunks {
  output:
  stdout raw_ensembl_ranges

  """
  rnac upi-ranges ${params.ftp_export.ensembl.chunk_size}
  """
}

raw_ensembl_ranges
  .splitCsv()
  .into { ensembl_ranges }

process ensembl_export_chunk {
  publishDir "${params.ftp_export.publish}/json/", mode: 'copy'

  input:
  set val(min), val(max) from ensembl_ranges
  file schema from Channel.fromPath('files/ftp-export/ensembl/schema.json')
  file query from Channel.fromPath('files/ftp-export/ensembl/ensembl-xrefs.sql')

  output:
  file(result) into __ensembl_export

  script:
  result = "ensembl-xref-$min-${max}.json"
  """
  psql -f $query --variable min=$min --variable max=$max "$PGDATABASE" > raw_xrefs.json
  rnac ftp-export ensembl --schema=$schema raw_xrefs.json $result
  """
}

process rfam_go_matches {
  publishDir "${params.ftp_export.publish}/go_annotations/", mode: 'copy'

  input:
  file query from Channel.fromPath('files/ftp-export/go_annotations/rnacentral_rfam_annotations.sql')

  output:
  file "rnacentral_rfam_annotations.tsv.gz" into __go_annotations

  """
  psql -f "$query" "$PGDATABASE" > raw_go.tsv
  rnac ftp-export rfam-go-annotations raw_go.tsv - |\
    gzip > rnacentral_rfam_annotations.tsv.gz
  """
}

process find_genome_coordinate_jobs {
  input:
  file query from Channel.fromPath('files/ftp-export/genome_coordinates/known-coordinates.sql')

  output:
  file('coordinates.txt') into species_to_format

  """
  psql -f $query $PGDATABASE > coordinates.txt
  """
}

species_to_format
  .splitCsv()
  .combine(Channel.fromPath('files/ftp-export/genome_coordinates/query.sql'))
  .into {
    coordinates_to_fetch
  }


process coordinate_readme {
  publishDir "${params.ftp_export.publish}/genome_coordinates/", mode: 'copy'

  input:
  file raw from Channel.fromPath('files/ftp-export/genome_coordinates/readme.mkd')

  output:
  file('readme.txt') into __coordinate_readmes

  """
  cat $raw > readme.txt
  """
}


process fetch_raw_coordinate_data {
  input:
  set val(assembly), val(species), val(taxid), file(query) from coordinates_to_fetch

  output:
  set val(assembly), val(species), file('result.json') into raw_coordinates

  """
  psql -v "taxid=$taxid" -v "assembly_id='$assembly'" -f $query "$PGDATABASE" > result.json
  """
}

raw_coordinates.into { bed_coordinates; gff_coordinates }

// process format_bed_coordinates {
//   publishDir "${params.ftp_export.publish}/genome_coordinates/", mode: 'copy'

//   input:
//   set val assembly, val species, file(raw_data) from bed_coordinates

//   output:
//   set val(assembly), file(result) into bed_files

//   script:
//   result = "${species}.${assembly}.bed.gz"
//   """
//   rnac ftp-export coordiantes as-bed $raw_data |\
//   sort -k1,1 -k2,2n |\
//   gzip > $result
//   """
// }

// process generate_big_bed {
//   publishDir "${params.ftp_export.publish}/genome_coordinates/", mode: 'copy'

//   input:
//   set val assembly, file bed_file from bed_files

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
  publishDir "${params.ftp_export.publish}/genome_coordinates/", mode: 'copy'

  input:
  set val(assembly), val(species), file(raw_data) from gff_coordinates

  output:
  file result into gff3_files

  script:
  result = "${species}.${assembly}.gff3.gz"
  """
  rnac ftp-export coordinates as-gff3 $raw_data - | gzip > $result
  """
}
