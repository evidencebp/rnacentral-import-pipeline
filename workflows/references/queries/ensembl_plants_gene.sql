-- ENSEMBL PLANTS
select
    gene,
    external_id,
    upi,
    taxid
from xref x
join rnc_accessions ra
on
	ra.accession = x.ac
where
	x.deleted = 'N'
	and ra."database" in ('ENSEMBL_PLANTS')
;
