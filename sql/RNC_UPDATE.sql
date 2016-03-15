-- Copyright [2009-2014] EMBL-European Bioinformatics Institute
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--      http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

set define off

create or replace PACKAGE RNC_UPDATE AS

  /*
    This is the main entry point for importing new data into the RNAcentral database.
  */
  PROCEDURE new_update(p_release_type IN RNACEN.rnc_release.release_type%TYPE DEFAULT 'F');

  PROCEDURE update_literature_references;

  PROCEDURE update_rnc_accessions;

END RNC_UPDATE;
/
create or replace PACKAGE BODY RNC_UPDATE AS



  /*
  * Update rnc_accessions by merging new data from load_rnc_accessions.
  */
  PROCEDURE update_rnc_accessions

  IS
  BEGIN

    DBMS_OUTPUT.put_line('Updating rnc_accessions');

    EXECUTE IMMEDIATE 'CREATE INDEX "RNACEN"."LOAD_RNC_ACCESSIONS$ACCESSION" ON LOAD_RNC_ACCESSIONS (ACCESSION) PARALLEL TABLESPACE "RNACEN_IND"';
    EXECUTE IMMEDIATE 'ALTER INDEX "RNACEN"."LOAD_RNC_ACCESSIONS$ACCESSION" NOPARALLEL';

    MERGE INTO rnc_accessions t1
    --ignore duplicates
    USING (SELECT * FROM load_rnc_accessions) t2
    ON (t1.accession = t2.accession)
    WHEN MATCHED THEN UPDATE SET
      t1.division=t2.division,
      t1.keywords=t2.keywords,
      t1.description=t2.description,
      t1.species=t2.species,
      t1.common_name=t2.common_name,
      t1.organelle=t2.organelle,
      t1.classification=t2.classification,
      t1.project=t2.project,
      t1.allele=t2.allele,
      t1.anticodon=t2.anticodon,
      t1.chromosome=t2.chromosome,
      t1.experiment=t2.experiment,
      t1.function=t2.function,
      t1.gene=t2.gene,
      t1.gene_synonym=t2.gene_synonym,
      t1.inference=t2.inference,
      t1.locus_tag=t2.locus_tag,
      t1.map=t2.map,
      t1.mol_type=t2.mol_type,
      t1.ncRNA_class=t2.ncRNA_class,
      t1.note=t2.note,
      t1.old_locus_tag=t2.old_locus_tag,
      t1.operon=t2.operon,
      t1.product=t2.product,
      t1.pseudogene=t2.pseudogene,
      t1.standard_name=t2.standard_name,
      t1.is_composite=t2.is_composite,
      t1.non_coding_id=t2.non_coding_id,
      t1.database=t2.database,
      t1.external_id=t2.external_id,
      t1.optional_id=t2.optional_id,
      t1.db_xref=t2.db_xref
    WHEN NOT MATCHED THEN INSERT
    (
      t1.accession,
      t1.parent_ac,
      t1.seq_version,
      t1.feature_start,
      t1.feature_end,
      t1.feature_name,
      t1.ordinal,
      t1.division,
      t1.keywords,
      t1.description,
      t1.species,
      t1.common_name,
      t1.organelle,
      t1.classification,
      t1.project,
      t1.allele,
      t1.anticodon,
      t1.chromosome,
      t1.experiment,
      t1.function,
      t1.gene,
      t1.gene_synonym,
      t1.inference,
      t1.locus_tag,
      t1.map,
      t1.mol_type,
      t1.ncRNA_class,
      t1.note,
      t1.old_locus_tag,
      t1.operon,
      t1.product,
      t1.pseudogene,
      t1.standard_name,
      t1.is_composite,
      t1.non_coding_id,
      t1.database,
      t1.external_id,
      t1.optional_id,
      t1.db_xref
    )
    VALUES
    (
      t2.accession,
      t2.parent_ac,
      t2.seq_version,
      t2.feature_start,
      t2.feature_end,
      t2.feature_name,
      t2.ordinal,
      t2.division,
      t2.keywords,
      t2.description,
      t2.species,
      t2.common_name,
      t2.organelle,
      t2.classification,
      t2.project,
      t2.allele,
      t2.anticodon,
      t2.chromosome,
      t2.experiment,
      t2.function,
      t2.gene,
      t2.gene_synonym,
      t2.inference,
      t2.locus_tag,
      t2.map,
      t2.mol_type,
      t2.ncRNA_class,
      t2.note,
      t2.old_locus_tag,
      t2.operon,
      t2.product,
      t2.pseudogene,
      t2.standard_name,
      t2.is_composite,
      t2.non_coding_id,
      t2.database,
      t2.external_id,
      t2.optional_id,
      t2.db_xref
    );

    COMMIT;

    EXECUTE IMMEDIATE 'DROP INDEX LOAD_RNC_ACCESSIONS$ACCESSION';

    BEGIN
      DBMS_STATS.GATHER_TABLE_STATS ( OWNNAME => 'RNACEN', TABNAME => 'rnc_accessions', ESTIMATE_PERCENT => 10 );
    END;

    DBMS_OUTPUT.put_line('rnc_accessions updated');

  END update_rnc_accessions;


  /*
  * Insert non-redundant literature references from the staging table into
  * the main table.
  */
  PROCEDURE update_literature_references
  IS

  BEGIN

    -- update rnc_references table
    INSERT INTO rnc_references
    (
      md5,
      location,

      authors,
      title,
      pmid,
      doi
    )

    SELECT
      /*+ PARALLEL */
      in_md5,
      in_location,
      in_my_authors,
      in_title,
      in_pmid,
      in_doi

    FROM
      (
      WITH
        distinct_new_refs AS

        (
          SELECT /*+ PARALLEL */ DISTINCT
            md5,
            location,
            useful_clob_object(authors) MY_AUTHORS,
            title,
            pmid,
            doi
          FROM

            load_rnc_references
         )
      SELECT

        l.md5 in_md5,
        l.location in_location,
        TREAT(l.MY_AUTHORS AS USEFUL_CLOB_OBJECT).UCO AS in_my_authors,
        l.title in_title,
        l.pmid in_pmid,
        l.doi in_doi
      FROM
        distinct_new_refs l,
        rnc_references p
     WHERE p.md5 (+) = l.md5 AND p.md5 IS NULL

      );


    commit;

    -- update rnc_reference_map table
    MERGE INTO rnc_reference_map t1
    USING (select t3.ACCESSION, t4.ID from load_rnc_references t3, rnc_references t4 where t3.md5 = t4.md5) t2
		ON (t1.ACCESSION = t2.ACCESSION and t1.reference_id=t2.id)
		WHEN NOT MATCHED THEN INSERT
		(
  		t1.accession,
			t1.reference_id
		)

		VALUES

		(
  		t2.accession,
			t2.id
		);
    COMMIT;

    EXECUTE IMMEDIATE 'TRUNCATE TABLE load_rnc_references DROP STORAGE';

    DBMS_OUTPUT.put_line('Literature references updated');

  END update_literature_references;




  /*
  * Move the data for the specified database into the staging table.
  */
  PROCEDURE move_staging_data (
    p_in_dbid IN RNACEN.rnc_database.ID%TYPE
  )
  IS
  BEGIN

		EXECUTE IMMEDIATE 'TRUNCATE TABLE load_rnacentral DROP STORAGE';


		INSERT INTO load_rnacentral (
      SELECT CRC64,
             LEN,
             SEQ_SHORT,
             SEQ_LONG,

             DATABASE,
             AC,
             OPTIONAL_ID,
             VERSION,
             TAXID,
             MD5
      FROM load_rnacentral_all d1, rnc_database d2

      WHERE d1.DATABASE = d2.descr AND d2.ID = p_in_dbid
    );

    COMMIT;

  END move_staging_data;


  /*
  * Create a new release for the specified database.
  */
  PROCEDURE create_release (
    p_in_dbid IN RNACEN.rnc_database.ID%TYPE,

    p_release_type IN RNACEN.rnc_release.release_type%TYPE
  )
  IS
    v_next_release INTEGER;
  BEGIN

    SELECT count(*) + 1 INTO v_next_release FROM rnc_release;


    DBMS_OUTPUT.put_line('Creating new release for database ' || TO_CHAR(p_in_dbid));

    INSERT INTO rnc_release
      (ID,

       dbid,
       release_date,
       release_type,
       status,
       rnc_release.TIMESTAMP,
       userstamp,
       descr,
       force_load)

    VALUES
      (
      v_next_release,
      p_in_dbid ,

      (SELECT to_char(trunc(SYSDATE),'dd-MON-yy') FROM dual),
      p_release_type,
      'L',
      (SELECT to_char(trunc(SYSDATE),'dd-MON-yy') FROM dual),
      'auto',
      '',
      'N'
    );


    COMMIT;

  END create_release;


  /*
  * Create new releases for all databases mentioned in the staging table.
  */
  PROCEDURE prepare_releases(
    p_release_type IN RNACEN.rnc_release.release_type%TYPE
  )
  IS
    CURSOR q
    IS

      SELECT distinct
        d2.id

      FROM
          load_rnacentral_all d1,
          rnc_database d2
      WHERE
        d1.DATABASE = d2.descr;
      v_count_existing_releases INTEGER;
  BEGIN

    SELECT count(*)
    INTO v_count_existing_releases
    FROM rnc_release

    WHERE status = 'L';


    IF (v_count_existing_releases > 0) THEN
      DBMS_OUTPUT.put_line('Found releases to be loaded');
      RETURN;
    END IF;

    DBMS_OUTPUT.put_line('Preparing the release table');

    FOR v_db IN q
    LOOP
      rnc_update.create_release(p_in_dbid => v_db.ID, p_release_type => p_release_type);
    END LOOP;



  END prepare_releases;

  /*
  * Set release status as 'Done' in rnc_release and update 'current_release' in
  * RNC_database.
  */
  PROCEDURE mark_as_done(
    p_in_dbid         IN RNACEN.rnc_database.ID%TYPE,
    p_in_load_release IN RNACEN.rnc_release.id%TYPE)
  IS
  BEGIN



    EXECUTE IMMEDIATE 'ALTER SESSION DISABLE PARALLEL DML';
    -- the next statement causes ORA-12838 without disabling parallel DML
    RNACEN.release.set_release_status( p_in_load_release, 'D' );
    RNACEN.DATABASE.set_current_release( p_in_dbid, p_in_load_release );
    COMMIT;
    EXECUTE IMMEDIATE 'ALTER SESSION ENABLE PARALLEL DML';

  END mark_as_done;

  /*
    Load one release into the database.
  */

  PROCEDURE load_release(

    p_in_dbid         IN RNACEN.rnc_database.id%TYPE,
    p_in_load_release IN RNACEN.rnc_release.id%TYPE)
  IS
    v_previous_release RNACEN.rnc_release.ID%TYPE;
    v_release_type RNACEN.rnc_release.release_type%TYPE;
  BEGIN

    DBMS_OUTPUT.PUT_LINE('Loading release: ' || p_in_load_release);

    -- initial logging
    RNC_LOGGING.log_release_start(p_in_dbid, p_in_load_release);


    -- load sequences

    RNC_LOAD_RNA.load_rna(p_in_dbid, p_in_load_release);

    -- load xrefs
    v_release_type := RNACEN.release.get_release_type(p_in_load_release);
    v_previous_release := RNACEN.release.get_previous_release(p_in_dbid, p_in_load_release);
    IF v_release_type = 'F' THEN
      RNC_LOAD_XREF.load_xref(v_previous_release, p_in_dbid);
    elsif v_release_type = 'I' THEN
      RNC_LOAD_XREF_INCREMENTAL.load_xref_incremental(v_previous_release, p_in_dbid);
    END IF;


    mark_as_done(p_in_dbid, p_in_load_release);


    RNC_LOGGING.log_release_end(p_in_dbid, p_in_load_release, v_previous_release);

    COMMIT;

  END load_release;


  /*
  * All xref ids are reset during Full updates because the xrefs
  * are imported using Partition Exchange Loading.
  * This operation is harmless because the ids are only used
  * by the Django web code.
  */

  PROCEDURE verify_xref_id_not_null
  AS
    v_count NUMBER;
  BEGIN
    SELECT count(*) INTO v_count FROM xref WHERE id IS NULL;
    IF v_count > 0 THEN

      -- update all id values
      UPDATE xref SET id = XREF_PK_SEQ.nextval;
      COMMIT;

    END IF;

  END verify_xref_id_not_null;


  /*
    Iterate over all releases with status 'L' and load them into the database.
  */

  PROCEDURE new_update (
    p_release_type IN RNACEN.rnc_release.release_type%TYPE DEFAULT 'F'
  )
  IS

    CURSOR c_load
    IS
      SELECT
        dbid,
        id,
        release_type,
        release_date,
        force_load

      FROM
          RNACEN.rnc_release
      WHERE
        status = 'L'
      ORDER BY

        ID;
  BEGIN

    DBMS_OUTPUT.put_line('Launching an update');

    EXECUTE IMMEDIATE 'CREATE INDEX "RNACEN"."LOAD_RNACENTRAL_ALL$DATABASE" ON LOAD_RNACENTRAL_ALL (DATABASE) PARALLEL TABLESPACE "RNACEN_IND"';
    EXECUTE IMMEDIATE 'ALTER INDEX "RNACEN"."LOAD_RNACENTRAL_ALL$DATABASE" NOPARALLEL';

    prepare_releases(p_release_type);

    FOR v_load IN c_load
    LOOP
      move_staging_data(p_in_dbid => v_load.dbid);
      load_release(
        p_in_dbid         => v_load.dbid,
        P_in_load_release => v_load.ID

      );
    END LOOP;

    EXECUTE IMMEDIATE 'DROP INDEX "RNACEN"."LOAD_RNACENTRAL_ALL$DATABASE"';

    verify_xref_id_not_null();

    rnc_healthchecks.run_healthchecks();

  END new_update;


END RNC_UPDATE;
/
set define on
