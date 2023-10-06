COPY (
  SELECT
    ensembl_url,
    assembly_id,
    taxid,
    division
  FROM ensembl_assembly
  WHERE
    division NOT IN ('EnsemblProtists')
) TO STDOUT CSV;
