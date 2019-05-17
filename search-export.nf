#!/usr/bin/env nextflow

// This is used to provide a temporary directory publish to. We publish here
// and then at the we publish everything at once. This prevents writing part of
// the data in the case one job fails while already succeeded.
def tmp = "mktemp -d -p ${workDir}".execute().text.trim()

process find_chunks {
  output:
  file('ranges.txt') into raw_ranges

  script:
  """
  rnac upi-ranges ${params.search_export.max_entries} ranges.txt
  """
}

raw_ranges
  .splitCsv()
  .combine(Channel.fromPath('files/search-export/query.sql'))
  .set { ranges }

process fetch_metdata {
  input:
  file('query*.sql') from Channel.fromPath('files/search-export/metadata/*.sql').collect()

  output:
  file("metadata.json") into metadata

  """
  find . -name '*.sql' | xargs -I {} psql -v ON_ERROR_STOP=1 -f "{}" "$PGDATABASE" >> metadata.json
  """
}

process export_search_json {
  // beforeScript 'slack db-work search-export || true'
  // afterScript 'slack db-done search-export || true'
  maxForks params.search_export.max_forks
  echo true

  input:
  set val(tablename), val(min), val(max), file(query) from ranges

  output:
  set val(min), val(max), file('search.json') into raw_json

  script:
  """
  psql -v ON_ERROR_STOP=1 --variable min=$min --variable max=$max -f "$query" "$PGDATABASE" > search.json
  """
}

raw_json
  .combine(metadata)
  .set { search_json }

process export_chunk {
  memory params.search_export.memory
  publishDir "${tmp}/", mode: 'copy'

  input:
  set val(min), val(max), file(json), file(metadata) from search_json

  output:
  file("${xml}.gz") into search_chunks
  file "count" into search_counts

  script:
  def xml = "xml4dbdumps__${min}__${max}.xml"
  """
  rnac search-export as-xml ${json} ${metadata} ${xml} count
  xmllint ${xml} --schema ${params.search_export.schema} --stream
  gzip ${xml}
  """
}

process create_release_note {
  input:
  file('count*') from search_counts.collect()

  output:
  file 'release_note.txt' into release_note

  script:
  """
  rnac search-export release-note ${params.release} release_note.txt count*
  """
}

// At this point we should be able to safely move data into the final location.
// This deletes the old data and then moves the new data in place.
process atomic_publish {
  input:
  file('release_note.txt') from release_note
  file(xml) from search_chunks.collect()

  script:
  def publish = params.search_export.publish
  def remote = (publish.host ? "$publish.host:" : "") + publish.path
  """
  if [[ -n "$publish.host" ]]; then
    ssh "$publish.host" 'mkdir -p $publish.path' || true
    ssh "$publish.host" 'rm -r $publish.path/*' || true
  else
    mkdir -p "$publish.path" || true
    rm "$publish.path/*"
  fi

  scp ${xml} 'release_note.txt' $remote
  """
}
