drop table if exists upis_to_precompute;

create table upis_to_precompute as
select distinct
  xref.upi
from xref
left join rnc_rna_precomputed pre
on
  pre.upi = xref.upi
  and pre.taxid = xref.taxid
where
  pre.id is null
  or xref.last > pre.last_release
;

alter table upis_to_precompute
  add constraint fk_to_precompute__upi FOREIGN KEY (upi) REFERENCES rna(upi),
  add column id bigserial primary key
;
