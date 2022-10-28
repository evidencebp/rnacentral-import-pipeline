process fetch_data {
  queue 'datamover'
  container ''
  errorStrategy 'ignore'

  input:
    path("base_dir")

  output:
  path('tsv_files')

  """
  mkdir tsv_files
  find $base_dir -type f .. | xargs -I {} -P 10 cp {} tsv_files
  """
}

process fetch_lookup {
  queue 'short'

  input:
    path (query)

  output:
    path("lookup_dump.csv")

    """
    psql -f $query $PGDATABASE > lookup_dump.csv
    """
}


process parse_tsvs {
  memory 24.GB

  input:
  path(tsvs)

  output:
  path('chunk_*')

  """
  expression-parse parse -i $tsvs -o all_genes.csv
  split -n l/10 all_genes.csv chunk_
  """

}

process lookup_genes {

  input:
    path(lookup)
    path(genes)

  output:
    path('*.csv')

  """
  expression-parse lookup -g $genes -l $lookup -o exp_parse_stage2.json
  rnac expressionatlas parse exp_parse_stage2.json .
  """
}


workflow expressionatlas {

  emit: data
  main:

  if( params.databases.expressionatlas.run ) {
    Channel.fromPath('files/import-data/expressionatlas/lookup-dump-query.sql') | set { lookup_sql }
    Channel.fromPath($params.databases.expressionatlas.remote) | set { tsv_path }
    lookup_sql | fetch_lookup | set { lookup }
    tsv_path \
    | fetch_data \
    | filter { tsv_name ->
      !params.databases.expressionatlas.exclude.any {p -> tsv_name.baseName =~ p}
    } \
    | parse_tsvs \
    | set { genes }

   lookup_genes(genes, lookup) \
   | collectFile() {csvfile -> [csvfile.name, csvfile.text]} \
   | set { data }

  }
  else {
    Channel.empty() | set { data }
  }

}
