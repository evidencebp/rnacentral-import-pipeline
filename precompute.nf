#!/usr/bin/env nextflow

process find_chunks {
  output:
  stdout raw_ranges

  """
  rnac upi-ranges ${params.precompute.max_entries}
  """
}

raw_ranges
  .splitCsv()
  .combine(Channel.fromPath('files/precompute/query.sql'))
  .into { ranges }

process precompute_range {
  beforeScript 'bin/slack db-work precompute-range || true'
  afterScript 'bin/slack db-done precompute-range || true'
  maxForks params.precompute.maxForks

  input:
  set val(min), val(max), file(query) from ranges

  output:
  file 'precompute.csv' into precompute_results
  file 'qa.csv' into qa_results

  """
  psql --variable min=$min --variable max=$max -f "$query" "$PGDATABASE" |\
    rnac precompute from-file -
  """
}

process load_precomputed_data {
  beforeScript 'bin/slack db-work loading-precompute || true'
  afterScript 'bin/slack db-done loading-precompute || true'

  input:
  file('result*.csv') from precompute_results.collect()
  file('qa*.csv') from qa_results.collect()
  file pre_ctl from Channel.fromPath('files/precompute/load.ctl')
  file qa_ctl from Channel.fromPath('files/precompute/qa.ctl')

  """
  cat result*.csv | pgloader $pre_ctl
  cat qa*.csv | pgloader $qa_ctl
  """
}
