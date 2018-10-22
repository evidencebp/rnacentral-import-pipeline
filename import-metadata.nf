#!/usr/bin/env nextflow

Channel.fromFilePairs("files/import-metadata/rfam/*.{ctl,sql}")
  .map { it[1] }
  .set { rfam_files }

def as_mysql_cmd = { db ->
  "mysql --host ${db.host} --port ${db.port} --user ${db.user}"
}

process import_rfam_metadata {
  input:
  set file(ctl), file(sql) from rfam_files

  script:
  filename = ctl.getName()
  name = filename.take(filename.lastIndexOf('.'))
  """
  set -o pipefail

  ${as_mysql_cmd(params.databases.rfam.mysql)} --database ${params.databases.rfam.mysql.db_name} < $sql > data.tsv
  rnac rfam $name data.tsv - | pgloader $ctl
  """
}

Channel.fromPath('files/import-metadata/ensembl/metadata/*.sql')
  .map { f -> f.getName().take(f.getName().lastIndexOf('.')) }
  .collectFile(name: "possible-data.txt", newLine: true)
  .set { ensembl_possible }

Channel.from(params.databases.ensembl.mysql, params.databases.ensembl_genomes.mysql)
  .combine(Channel.fromPath('files/import-metadata/ensembl/analyzed.sql'))
  .combine(ensembl_possible)
  .set { ensembl_info }

process find_ensembl_databases {
  input:
  set val(mysql), file(imported_sql), file(possible) from ensembl_info

  output:
  set val(mysql), file('selected.csv') into ensembl_databases

  """
  set -o pipefail

  psql -v ON_ERROR_STOP=1 -f "$imported_sql" "$PGDATABASE" > done.csv
  echo 'show databases' | ${as_mysql_cmd(mysql)} > dbs.txt
  rnac ensembl select-tasks dbs.txt $possible done.csv > selected.csv
  """
}

ensembl_databases
  .flatMap { mysql, csv ->
    data = []
    csv.eachLine { line -> data << ([mysql] + line.tokenize(',')) }
    data
  }
  .map { mysql, name, db -> [mysql, name, db, file("files/import-metadata/ensembl/metadata/${name}.sql")] }
  .set { ensembl_metadata_dbs }

process fetch_internal_ensembl_data {
  maxForks params.import_metadata.ensembl.max_forks

  input:
  set val(mysql), val(name), val(db), file(sql) from ensembl_metadata_dbs

  output:
  set val(name), val(db) file('data.csv') into raw_ensembl_metadata

  script:
  """
  ${as_mysql_cmd(mysql)} -N --database $db < $sql > data.tsv
  if [[ -s data.tsv ]]; then
    if [[ "$name" -eq "coordinates" ]]; then
      touch data.csv
    else
      echo 1>&2 "No data produced for $name $db"
      exit 1
    fi
  fi
  rnac ensembl $name data.tsv data.csv
  """
}

raw_ensembl_metadata
  .filter { n, d, f -> !f.isEmpty() }
  .groupTuple()
  .map { name, dbs, data_files ->
    [file("files/import-metadata/ensembl/metadata/${name}.ctl"), data_files, dbs]
  }
  .combine(Channel.fromPath('files/import-metadata/ensembl/mark-analyzed.ctl'))
  . set { ensembl_loadable }

process import_ensembl_data {
  echo true

  input:
  set file(ctl), file('data*.csv'), val(dbs), file(mark_ctl) from ensembl_loadable

  script:
  file("imported.txt").withWriter { writer ->
    dbs.each { db -> writer << "${name},${db}\n" }
  }
  """
  split-and-load $ctl 'data*.csv' ${params.import_data.chunk_size} data

  cp $mark_ctl local_$mark_ctl
  pgloader --on-error-stop local_$mark_ctl
  """
}
