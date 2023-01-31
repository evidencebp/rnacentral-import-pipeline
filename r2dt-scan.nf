#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include { r2dt } from './workflows/r2dt'


process parse_gtrnadb_model {

  input:
    path(model_path)
  output:
    path("model_data.csv")

  script:
    """
    bps=`/rna/infernal-1.1.2/bin/cmstat $model_path | awk ' /^[^#]/ { print $8 }'`
    rnac r2dt model-info gtrnadb $model_path $bps model_data.csv
    """
}

process parse_ribovision_models {

  input:
    val(ribovision_metadata_url)



  output:
    path("model_data.csv")

  script:
  """
  wget $ribovision_metadata_url
  cmstat /rna/r2dt/data/ribovision-lsu/cms/all.cm | awk '/^[^#]/ {sep=","; printf "%s%s%s%s%s\n",$2,sep,$6,sep,$8}' > basepair_length_lsu
  cmstat /rna/r2dt/data/ribovision-ssu/cms/all.cm | awk '/^[^#]/ {sep=","; printf "%s%s%s%s%s\n",$2,sep,$6,sep,$8}' > basepair_length_ssu
  cat basepair_length_lsu basepair_length_ssu > basepair_length

  rnac r2dt model-info ribovision metadata.tsv model_data_us.csv
  sort -k 1 model_data.csv > model_data_s.csv
  join -t","  model_data_s.csv basepair_length -o 1.1,1.2,1.3,1.4,1.5,1.6,2.2,2.3 > model_data.csv
  """

}

process parse_rnasep_models {

  input:
    val(rnasep_metadata_url)

  output:
    path("model_data.csv")

  script:
  """
  cmstat /rna/r2dt/data/rnasep/cms/all.cm | awk '/^[^#]/ {sep=","; printf "%s%s%s%s%s\n",$2,sep,$6,sep,$8}' > length_basepair
  wget $rnasep_metadata_url
  sed -i 's/\\tNRC-1\\t/\\t/g' metadata.tsv
  rnac r2dt model-info rnase-p metadata.tsv model_data_us.csv
  sort -k1 model_data_us.csv > model_data_s.csv
  join -t","  model_data_s.csv length_basepair -o 1.1,1.2,1.3,1.4,1.5,1.6,2.2,2.3 > model_data.csv
  """

}

process parse_rfam_models {

  input:
    path(all_models)
  output:
    path("model_data.csv")

  script:
  """
  cmstat $all_models | awk '/^[^#]/ {sep=","; printf "%s%s%s\n",$3,sep,$8}' > basepairs
  rnac r2dt model-info rfam $all_models $PGDATABASE model_data_nbp.csv
  join -t","  model_data_nbp.csv basepairs -o 1.1,1.2,1.3,1.4,1.5,1.6,1.7,2.2 > model_data.csv
  """
}


process parse_crw_models {

  input:
    tuple path(all_models), val(metadata)
  output:
    path("model_data.csv")

  script:
  """
  wget $metadata -O metadata.tsv
  sed -i 's/taxid  rna_type/taxid\trna_type/g' metadata.tsv
  cmstat $all_models | awk '/^[^#]/ {sep=","; printf "%s%s%s\n",$2,sep,$8}' > basepairs
  rnac r2dt model-info crw $all_models metadata.tsv model_data_nbp.csv
  join -t","  model_data_nbp.csv basepairs -o 1.1,1.2,1.3,1.4,1.5,1.6,1.7,2.2 > model_data.csv

  """
}

process load_models {

  input:
    path(all_data)
    path(ctl)

  output:
    val('models loaded')

  script:
  """
  split-and-load $ctl $all_data ${params.import_data.chunk_size}
  """
}





workflow {
  rfam_models = Channel.of("$baseDir/singularity/bind/r2dt/data/cms/rfam/all.cm")
  crw_models = Channel.of("$baseDir/singularity/bind/r2dt/data/cms/crw/all.cm")
  crw_metadata = Channel.of("https://raw.githubusercontent.com/RNAcentral/R2DT/v1.3/data/crw-metadata.tsv")
  gtrnadb_models = Channel.fromPath("$baseDir/singularity/bind/r2dt/data/cms/gtrnadb/*.cm")
  ribovision_lsu_metadata_url = Channel.of("https://raw.githubusercontent.com/RNAcentral/R2DT/v1.3/data/ribovision-lsu/metadata.tsv")
  ribovision_ssu_metadata_url = Channel.of("https://raw.githubusercontent.com/RNAcentral/R2DT/v1.3/data/ribovision-ssu/metadata.tsv")

  rnasep_metadata_url = Channel.of("https://raw.githubusercontent.com/RNAcentral/R2DT/v1.3/data/rnasep/metadata.tsv")

  load_ctl = Channel.of("$baseDir/files/r2dt/load-models.ctl")

  rfam_models | parse_rfam_models | set { rfam_data }
  crw_models.combine(crw_metadata) | parse_crw_models | set { crw_data }
  gtrnadb_models | parse_gtrnadb_model | collectFile() {csvfile -> [csvfile.name, csvfile.text]} | set { gtrnadb_data }
  ribovision_lsu_metadata_url.mix(ribovision_ssu_metadata_url) | parse_ribovision_models | set {ribovision_data }
  rnasep_metadata_url | parse_rnasep_models | set {rnasep_data}

  rfam_data.mix(crw_data, gtrnadb_data, ribovision_data, rnasep_data) | collectFile() {csvfile -> [csvfile.name, csvfile.text]} | set { all_data }


   load_models(all_data, load_ctl) | set { model_load }

   model_load | r2dt | set { done }

}
