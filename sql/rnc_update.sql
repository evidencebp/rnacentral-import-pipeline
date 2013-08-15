create or replace
PACKAGE BODY RNC_UPDATE AS

  /*
  * Create a new release for the specified database.
  */
  PROCEDURE create_release (
    p_in_dbid IN RNACEN.rnc_database.ID%TYPE
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
      'F',
      'L',
      (SELECT to_char(trunc(SYSDATE),'dd-MON-yy') FROM dual),
      'auto',
      '',
      'N'
    );

    --rnacen.DATABASE.set_current_release(p_in_dbid , v_next_release);


  END create_release;

  /*
  * Create new releases for all databases mentioned in the staging table.
  */
  PROCEDURE prepare_releases
  IS
    CURSOR q
    IS
      SELECT distinct
        d2.id
      FROM
          load_rnacentral d1,
          rnc_database d2
      WHERE
        d1.database = d2.descr;
  BEGIN

    DBMS_OUTPUT.put_line('Preparing the release table');

    FOR v_db IN q
    LOOP
      rnc_update.create_release(p_in_dbid => v_db.id);
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
    v_previous_release RNACEN.rnc_release.id%TYPE;
  BEGIN

    DBMS_OUTPUT.PUT_LINE('Loading release: ' || p_in_load_release);

    -- initial logging
    RNC_LOGGING.log_release_start(p_in_dbid, p_in_load_release);

    -- load sequences
    RNC_LOAD_RNA.load_rna(p_in_dbid, p_in_load_release);

    -- load xrefs
    v_previous_release := RNACEN.release.get_previous_release(p_in_dbid, p_in_load_release);
    RNC_LOAD_XREF.load_xref(v_previous_release, p_in_dbid);

    mark_as_done(p_in_dbid, p_in_load_release);

    RNC_LOGGING.log_release_end(p_in_dbid, p_in_load_release, v_previous_release);

  END load_release;

  /*
    Iterates over all releases with status 'L' and load them into the database.
  */
  PROCEDURE new_update
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
        id;
  BEGIN

    DBMS_OUTPUT.put_line('Launching an update');

    prepare_releases();

    FOR v_load IN c_load
    LOOP
      load_release(
        p_in_dbid         => v_load.dbid,
        P_in_load_release => v_load.id
      );
    END LOOP;

  END new_update;

END RNC_UPDATE;