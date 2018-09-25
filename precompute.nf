#!/usr/bin/env nextflow

queries = [
  all: 'files/precompute/methods/all.sql',
  by_database: 'files/precompute/methods/for-database.sql',
  using_release: 'files/precompute/methods/using-release.sql'
]

precompute_upi_queries = Channel.empty()

if (precompute.methods.all) {
  Channel
    .from([file(queries.all), []])
    .set { precompute_upi_queries }

} else if (precompute.methods.using_release) {
  Channel
    .from([file(queries.using_release), []])
    .set { precompute_upi_queries }

} else if (precompute.methods.by_database) {

  db_names = []
  params.precompute.methods.by_database.each { db ->
    db_names << "'${db.toUpperCase()}'"
  }
  db_names = db_names.join(', ')

  Channel
    .from([file(queries.by_database), [dbs: db_names]])
    .set { precompute_upi_queries }

} else {
  error "Have to choose a way to precompute"
}

process query_upis {
  input:
  set file(sql), val(variables) from precompute_upi_queries

  output:
  file('ranges.txt') raw_ranges

  script:
  variable_option = []
  variables.each { name, value ->
    variable_option << "-v ${name}=${value}"
  }
  """
  psql -f "$sql" ${variable_option.join(' ')} "$PGDATABASE"
  rnac upi-ranges --table-name ${table_name} ${params.precompute.max_entries} ranges.txt
  """
}

raw_ranges
  .splitCsv()
  .combine(Channel.fromPath('files/precompute/query.sql'))
  .set { ranges }

process precompute_range_query {
  beforeScript 'slack db-work precompute-range || true'
  afterScript 'slack db-done precompute-range || true'
  maxForks params.precompute.maxForks

  input:
  set val(min), val(max), file(query) from ranges

  output:
  file 'raw-precompute.json' into precompute_raw

  """
  psql --variable min=$min --variable max=$max -f "$query" '$PGDATABASE' > raw-precompute.json
  """
}

process precompute_range {
  memory '4 GB'

  input:
  file(raw) from precompute_raw

  output:
  file 'precompute.csv' into precompute_results
  file 'qa.csv' into qa_results

  """
  rnac precompute from-file $raw
  """
}

process load_precomputed_data {
  beforeScript 'slack db-work loading-precompute || true'
  afterScript 'slack db-done loading-precompute || true'

  input:
  file('precompute*.csv') from precompute_results.collect()
  file('qa*.csv') from qa_results.collect()
  file pre_ctl from Channel.fromPath('files/precompute/load.ctl')
  file qa_ctl from Channel.fromPath('files/precompute/qa.ctl')
  file post from Channel.fromPath('files/precompute/post-load.sql')

  // Use cp to copy the ctl files and not stageInMode because we don't want to
  // have to copy a large number of large files before running this. We only
  // need a copy of these two files in the local directory. This is because
  // pgloader will look at the location of the end of symlink when trying to
  // find files and not the current directory or where the symlink lives.
  """
  cp $pre_ctl _pre.ctl
  cp $qa_ctl _qa.ctl
  pgloader _pre.ctl
  pgloader _qa.ctl
  psql -f $post "$PGDATABASE"
  """
}
