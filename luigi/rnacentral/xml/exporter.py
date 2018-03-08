# -*- coding: utf-8 -*-

"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
from datetime import date

import xml.etree.cElementTree as ET

from .data import builder


BASE_SQL = """
SELECT
    json_build_object(
        'upi', rna.upi,
        'taxid', xref.taxid,
        'first_seen', array_agg(release1.timestamp),
        'last_seen', array_agg(release2.timestamp),
        'cross_references', array_agg(
            json_build_object(
                'name', acc."database",
                'external_id', acc.external_id,
                'optional_id', acc.optional_id,
                'accession', acc.accession,
                'non_coding_id', acc.non_coding_id,
                'parent_accession', acc.parent_ac || '.' || acc.seq_version
                )
            ),
        'description', (array_agg(pre.description))[1],
        'deleted', 'N',
        'length', (array_agg(rna.len))[1],
        'species', (array_agg(acc.species))[1],
        'organelles', array_agg(acc.organelle),
        'expert_dbs', array_agg(db.display_name),
        'rna_type', (array_agg(pre.rna_type))[1],
        'product', array_agg(acc.product),
        'md5', (array_agg(rna.md5))[1],
        'authors', array_agg(refs.authors),
        'journals', array_agg(refs.location),
        'pub_titles', array_agg(refs.title),
        'pub_ids', array_agg(refs.pmid),
        'dois', array_agg(refs.doi),
        'has_genomic_coordinates', cardinality(array_remove(array_agg(distinct coord.id), null)) > 0,
        'rfam_family_names', array_agg(models.short_name),
        'rfam_ids', array_agg(hits.rfam_model_id),
        'rfam_clans', array_agg(models.rfam_clan_id),
        'rfam_status', (array_remove(array_agg(pre.rfam_problems), ''))[1]::json,
        'tax_strings', array_agg(acc.classification),
        'functions', array_agg(acc.function),
        'genes', array_agg(acc.gene),
        'gene_synonyms', array_agg(acc.gene_synonym),
        'common_name', array_agg(acc.common_name),
        'notes', array_agg(acc.note),
        'locus_tags', array_agg(acc.locus_tag),
        'standard_names', array_agg(acc.standard_name),
        'products', array_agg(acc.product)
    )
FROM xref xref
JOIN rnc_accessions acc ON xref.ac = acc.accession
JOIN rnc_database db ON xref.dbid = db.id
JOIN rnc_release release1 on xref.created = release1.id
JOIN rnc_release release2 on xref.last = release2.id
JOIN rna rna on xref.upi = rna.upi
JOIN rnc_rna_precomputed pre on xref.upi = pre.upi and xref.taxid = pre.taxid
left join rnc_coordinates coord
on
    coord.accession = acc.accession
    and coord.name is not null
    and coord.name != ''
LEFT JOIN rnc_reference_map ref_map on ref_map.accession = acc.accession
LEFT JOIN rnc_references refs on refs.id = ref_map.reference_id
LEFT JOIN rfam_model_hits hits ON xref.upi = hits.upi
LEFT JOIN rfam_models models
ON hits.rfam_model_id = models.rfam_model_id
WHERE
  xref.deleted = 'N'
  and {terms}
group by rna.upi, xref.taxid
"""

SINGLE_SQL = BASE_SQL.format(
    terms="xref.upi = %(upi)s AND xref.taxid = %(taxid)s"
)

RANGE_SQL = BASE_SQL.format(terms="rna.id BETWEEN %(min_id)s AND %(max_id)s")


def export_range(cursor, min_id, max_id):
    """
    Generates a series of XML strings representing all entries in the given
    range of ids.
    """

    with cursor() as cur:
        cur.execute(RANGE_SQL, {'min_id': min_id, 'max_id': max_id})
        for result in cursor:
            data = json.loads(result[0])
            yield builder(data)


def export_upi(cursor, upi, taxid):
    """
    Will create a XmlEntry object for the given upi, taxid.
    """

    with cursor() as cur:
        cur.execute(SINGLE_SQL, {'upi': upi, 'taxid': taxid})
        result = list(cur)
        if not result:
            raise ValueError("Found no entries for %s_%s" % (upi, str(taxid)))
        return builder(result[0][0])


def as_document(results, handle):
    """
    This will create the required root XML element and place all the given
    XmlEntry objects as ElementTree.Element's in it. This then produces the
    string representation of that document which can be saved.
    """

    root = ET.Element('database')
    ET.SubElement(root, 'name', text='RNAcentral')
    ET.SubElement(
        root,
        'description',
        text='a database for non-protein coding RNA sequences'
    )
    ET.SubElement(root, 'release', text='1.0')

    timestamp = date.today.strftime('%d/%m/%Y')
    ET.SubElement(root, 'release_date', timestamp)

    count = 0
    count_element = ET.SubElement(root, 'entry_count')
    entries = ET.SubElement(root, 'entries')
    for result in results:
        entries.append(result.as_xml())
        count += 1

    if not count:
        raise ValueError("No entries found")

    count_element.text = count
    root.write(handle)
