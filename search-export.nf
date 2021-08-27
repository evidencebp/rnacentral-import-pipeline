#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include { sequences } from './workflows/search-export/sequences'
include { genes } from './workflows/search-export/genes'

process create_release_note {
  containerOptions "--contain --workdir $baseDir/work/tmp --bind $baseDir"

  input:
  path('count*')

  output:
  path('release_note.txt')

  script:
  """
  rnac search-export release-note ${params.release} release_note.txt count*
  """
}

// At this point we should be able to safely move data into the final location.
// This deletes the old data and then moves the new data in place.
process atomic_publish {
  container ''

  input:
  path('release_note.txt')
  path(xml)
  path(post)

  script:
  def publish = params.search_export.publish
  if (params.search_export.publish.host)
    """
    ssh "$publish.host" 'mkdir -p $publish.path' || true
    ssh "$publish.host" 'rm -r $publish.path/*' || true
    scp ${xml} 'release_note.txt' $publish.host:$publish.path
    psql -v ON_ERROR_STOP=1 -f "$post" "$PGDATABASE"
    """
  else
    """
    rm $publish.path/*
    cp ${xml} 'release_note.txt' $publish.path
    psql -v ON_ERROR_STOP=1 -f "$post" "$PGDATABASE"
    """
}

workflow search_export {
  Channel.fromPath('files/search-export/post-publish.sql') | set { post }

  sequences()

  genes(sequences.out.search_count, sequences.out.sequence_json)

  sequences.out.counts \
  | mix(genes.out.counts) \
  | collect \
  | create_release_note \
  | set { note }

  sequences.out.xml \
  | mix(genes.out.xml) \
  | collect \
  | set { xml }

  atomic_publish(note, xml, post)
}

workflow {
  search_export()
}
