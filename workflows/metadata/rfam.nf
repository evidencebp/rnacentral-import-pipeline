process generic {
  when { params.databases.ensembl.run || params.databases.rfam.run }

  input:
  tuple val(name), path(query)

  output:
  path('*.csv')

  script:
  def conn = params.connections.rfam
  """
  mysql \
    --host $conn.host \
    --database $conn.database \
    --user $conn.user \
    --port $conn.port \
    < $query > raw.tsv
  rnac rfam $name raw.tsv
  """
}

workflow rfam {
  emit: data
  main:
    Channel.fromPath('files/import-data/rfam/{clans,families,ontology-terms}.sql') \
    | map { fn -> [fn.name, fn] } \
    | generic \
    | flatten \
    | set { data }
}
