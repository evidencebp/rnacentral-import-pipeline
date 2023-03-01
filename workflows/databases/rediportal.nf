process build_rnc_bedfile {

  input:
    path(query)

  ouput:
    path("rnc_regions.bed")

  """
  set -euo pipefail
  psql -v ON_ERROR_STOP=1 -v "assembly_id=GRCh38" -f $puery "$PGDATABASE" > result.json

  rnac ftp-export coordinates as-bed result.json |\
  sort -k1,1 -k2,2n > rnc_regions_gene.bed
  bed-expander rnc_regions_gene.bed rnc_regions.bed
  """
}

process fetch_rediportal_bedfile {

  output:
    path("REDI_sorted.bed")

  """
  wget -O REDI_sorted_untabbed.bed $params.databases.rediportal.bed_remote
  awk 'BEGIN {OFS="\t"} {print $1,$2,$3,$4,$5,$6,$7}' REDI_sorted_untabbed.bed > REDI_sorted.bed
  """
}


process fetch_rediportal_metadata {

  output:
    path("TABLE1_hg38.txt")

  """
  curl $params.databases.rediportal.meta_remote | gzip -d > TABLE1_hg38.txt
  """
}

process intersect_rnc_rediportal {

  input:
    tuple path(rnc_bed), path(redi_bed), path(redi_meta)

  output:
    path("features.csv")

  """
  rnac rediportal parse $redi_bed $redi_meta $rnc_bed features.csv
  """
}

process load_rediportal {

  input:
    tuple path(features), path(ctl)

  """
  psql -v ON_ERROR_STOP=1 -f $ctl "$PGDATABASE"
  """

}

workflow rediportal {
  Channel.fromPath("files/ftp-export/genome_coordinates/query.sql") | set { region_query }
  Channel.fromPath("files/rediportal/load.ctl") | set { load_query }

  region_query | build_rnc_bedfile | set { rnc_bedfile }
  fetch_rediportal_metadata | set { redi_meta }
  fetch_rediportal_bedfile) | set {redi_bedfile }
  rnc_bedfile.combine(redi_meta, redi_bedfile) | intersect_rnc_rediportal \
  | combine(load_query) | load_rediportal




}
