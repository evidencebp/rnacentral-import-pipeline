nextflow.enable.dsl=2

process create_metadata {
    input:
    val(_flag)
    path(database)

    output:
    path("metadata_${database.baseName}")

    script:
    """
    litscan-metadata.py $database metadata_${database.baseName}
    """
}

process merge_metadata {
    publishDir "$baseDir/workflows/litscan/metadata/", mode: 'copy'

    input:
    file(results)

    output:
    path("merged_metadata")

    script:
    """
    if [[ -f $baseDir/workflows/litscan/metadata/rfam/extra-ids.txt ]]; then
      cat $baseDir/workflows/litscan/metadata/rfam/extra-ids.txt > merged_metadata
    fi

    cat $results | sort -fb | uniq -i >> merged_metadata
    """
}

process create_xml {
    memory '2GB'
    publishDir "$params.litscan_index", mode: 'copy'

    input:
    file(merged_metadata)

    output:
    path("metadata_*")

    script:
    """
    rm "$params.litscan_index"/metadata*
    litscan-create-xml-metadata.py $merged_metadata metadata_*
    """
}

process create_release_file {
    publishDir "$params.litscan_index", mode: 'copy'

    input:
    val(_flag)

    output:
    path("release_note.txt")

    script:
    """
    litscan-create-release-note-file.sh $params.litscan_index $params.release_version
    """
}

process load_database_table {
    input:
    path(metadata)
    path(ctl)

    script:
    """
    pgloader --on-error-stop $ctl
    """
}

workflow export_metadata {
    take: ready
    main:
      database = Channel.fromPath('workflows/litscan/results/*.txt')
      create_metadata(ready, database) | collect | merge_metadata | set{ metadata }

      create_xml(metadata) | create_release_file

      load = Channel.of("$baseDir/workflows/litscan/metadata/load-metadata.ctl")
      load_database_table(metadata, load)
}

workflow {
  export_metadata(Channel.of('ready'))
}
