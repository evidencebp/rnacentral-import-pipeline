nextflow.enable.dsl = 2

process fetch_data {
  when { !params.databases.plncdb.prefetch and params.databases.plncdb.run }

  containerOptions "--contain --bind $baseDir"

  output:
  path("data")

  """
  rnac plncdb fetch-data $params.databases.plncdb.urls data
  """
}

process parse_data {
  when { params.databases.plncdb.run }

  queue 'short'

  input:
  path data

  output:
  path('accessions.csv')
  path('features.csv')
  path('go_annotations.csv')
  path('interactions.csv')
  path('long_sequences.csv')
  path('references.csv')
  path('ref_ids.csv')
  path('regions.csv')
  path('related_sequences.csv')
  path('secondary_structure.csv')
  path('short_sequences.csv')
  path('terms.csv')

  """
  rnac notify step "Data parsing for PLncDB" $params.databases.plncdb.data_path$data
  rnac plncdb parse $params.databases.plncdb.data_path$data
  """
}

workflow plncdb {
  emit: data_files

  main:

  Channel.fromPath("$params.databases.plncdb.data_path/*", type:'dir') \
  | parse_data
  | collectFile
  | set { data_files }


}
