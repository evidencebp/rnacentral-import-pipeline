process quickgo_get {
  queue 'datamover'
  container ''

  output:
  path('data.gpa.gz')

  """
  scp $params.databases.quickgo.remote data.gpa.gz
  """
}



process quickgo_parse {
  memory { params.databases.quickgo.memory }

  input:
  path(data)

  output:
  path('*.csv')

  """
  gzip -d $data
  rnac quickgo parse data.gpa .
  """
}



workflow quickgo {

  emit: data

  main:
    if params.databases.quickgo.run {
      quickgo_get | quickgo_parse | set { data }
    }
    else {
      Channel.empty() | set { data }
    }


}
