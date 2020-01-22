COPY (
SELECT
  json_build_object(
    'rna_id', pre.id,
    'secondary', json_build_object(
      'has_secondary', true,
      'secondary_structure_model', models.model_name
      'secondary_structure_source', models.model_source
    )
  )
FROM rnc_secondary_structure_layout as layout
JOIN rnc_secondary_structure_layout_models as models
ON
  layout.model_id = models.id
JOIN rnc_rna_precomputed pre
ON
  pre.upi = layout.urs
WHERE
  pre.taxid is not null
  and layout.should_show = true
) TO STDOUT
