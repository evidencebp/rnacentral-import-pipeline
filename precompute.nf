#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include { repeats } from './workflows/repeats'

process build_precompute_context {
  input:
  path('species-repeats*')

  output:
  path('context')

  """
  mkdir repeat-tree
  mv species-repeats* repeat-tree
  pushd repeat-tree
  rnac repeats build-tree .
  popd
  mkdir context
  mv repeat-tree context
  """
}

process fetch_release_info {
  tag { "${query.baseName}" }
  when { params.precompute.run }
  containerOptions "--contain --workdir $baseDir/work/tmp --bind $baseDir"

  input:
  path(query)

  output:
  path('data.csv')

  """
  psql -v ON_ERROR_STOP=1 -f $query $PGDATABASE > raw
  sort -u raw > sorted.csv
  precompute max-release sorted.csv > data.csv
  """
}

process find_ranges {
  containerOptions "--contain --workdir $baseDir/work/tmp --bind $baseDir"

  input:
  tuple path(load), path('xref.csv'), path('precompute.csv')

  output:
  path('ranges.txt')

  """
  precompute select xref.csv precompute.csv to-load.csv
  psql \
    -v ON_ERROR_STOP=1 \
    -v tablename=${params.precompute.tablename} \
    -f $load "$PGDATABASE"
  rnac upi-ranges --table-name ${params.precompute.tablename} ${params.precompute.max_entries} ranges.txt
  """
}

process query_range {
  tag { "$min-$max" }
  beforeScript 'slack db-work precompute-range || true'
  afterScript 'slack db-done precompute-range || true'
  maxForks params.precompute.maxForks
  container ''

  input:
  tuple val(tablename), val(min), val(max), path(query)

  output:
  tuple val(min), val(max), path('raw-precompute.json')

  """
  psql \
    --variable ON_ERROR_STOP=1 \
    --variable tablename=${params.precompute.tablename} \
    --variable min=$min \
    --variable max=$max \
    -f "$query" \
    '$PGDATABASE' > raw-precompute.json
  """
}

process process_range {
  tag { "$min-$max" }
  memory params.precompute.range.memory
  containerOptions "--contain --workdir $baseDir/work/tmp --bind $baseDir"

  input:
  tuple val(min), val(max), path(raw), path(context)

  output:
  path 'precompute.csv', emit: data
  path 'qa.csv', emit: qa

  """
  rnac precompute from-file $context $raw
  """
}

process load_data {
  beforeScript 'slack db-work loading-precompute || true'
  afterScript 'slack db-done loading-precompute || true'
  container ''

  input:
  tuple path('precompute*.csv'), path('qa*.csv'), path(pre_ctl), path(qa_ctl), path(post)

  script:
  def tablename = params.precompute.tablename
  """
  split-and-load $pre_ctl 'precompute*.csv' ${params.import_data.chunk_size} precompute
  split-and-load $qa_ctl 'qa*.csv' ${params.import_data.chunk_size} qa
  psql -v ON_ERROR_STOP=1 -f $post "$PGDATABASE"
  psql -v ON_ERROR_STOP=1 -c 'DROP TABLE IF EXISTS $tablename' "$PGDATABASE"
  """
}

workflow precompute {
  main:
    Channel.fromPath('files/precompute/fetch-precompute-info.sql') | set { precompute_info_sql }
    Channel.fromPath('files/precompute/fetch-xref-info.sql') | set { xref_info_sql }
    Channel.fromPath('files/precompute/load-urs.sql') | set { load_sql }

    build_precompute_context(repeats()) | set { context }

    precompute_info_sql | fetch_release_info | set { precompute_info }
    xref_info_sql | fetch_release_info | set { xref_info }

    load_sql \
    | combine(precompute_info) \
    | combine(xref_info) \
    | find_ranges \
    | splitCsv \
    | combine(Channel.fromPath('files/precompute/query.sql')) \
    | query_range \
    | combine(context) \
    | process_range \

    process_range.out.data | collect | set { data }
    process_range.out.qa | collect | set { qa }

    data \
    | combine(qa) \
    | combine(Channel.fromPath('files/precompute/load.ctl')) \
    | combine(Channel.fromPath('files/precompute/qa.ctl')) \
    | combine(Channel.fromPath('files/precompute/post-load.sql')) \
    | load_data
}

workflow {
  precompute()
}
