process flybase {
  when: { params.databases.flybase.run }

  output:
  path('*.csv')

  """
  wget -O - ${params.databases.flybase.remote} | gzip -d > flybase.json
  rnac external flybase flybase.json .
  """
}