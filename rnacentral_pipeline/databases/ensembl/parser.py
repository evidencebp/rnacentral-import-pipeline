# -*- coding: utf-8 -*-

"""
Copyright [2010-2018] EMBL-European Bioinformatics Institute
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

import operator as op
import itertools as it

import attr

from rnacentral_pipeline.databases import data
from rnacentral_pipeline.databases.helpers import embl

from . import helpers
from .data import Context


def as_entry(record, gene, feature, context):
    """
    Turn the Record, Gene feature, transcript feature and Context into a Entry
    object for output.
    """

    species, common_name = helpers.organism_naming(record)
    xref_data = embl.xref_data(feature)

    entry = data.Entry(
        primary_id=helpers.primary_id(feature),
        accession=helpers.accession(feature),
        ncbi_tax_id=embl.taxid(record),
        database='ENSEMBL',
        sequence=embl.sequence(record, feature),
        exons=helpers.exons(record, feature),
        rna_type=helpers.rna_type(context.inference, feature, xref_data),
        url=helpers.url(feature),
        seq_version=helpers.seq_version(feature),
        lineage=embl.lineage(record),
        chromosome=helpers.chromosome(record),
        parent_accession=record.id,
        common_name=common_name,
        species=species,
        gene=embl.locus_tag(gene),
        locus_tag=embl.locus_tag(gene),
        optional_id=gene,
        note_data=helpers.note_data(feature),
        xref_data=xref_data,
        product=helpers.product(feature),
        references=helpers.references(),
        mol_type='genomic DNA',
        pseudogene='N',
        is_composite='N',
    )

    return attr.assoc(
        entry,
        description=helpers.description(entry)
    )


def parse(raw, family_file):
    """
    This will parse an EMBL file for all Ensembl Entries to import.
    """

    context = Context(family_file)
    key = op.itemgetter(0, 1)
    grouped = it.groupby(embl.transcripts(raw), key)
    for (record, gene), features in grouped:
        ncrnas = []
        for feature in features:
            if context.is_supressed(feature):
                continue
            if helpers.is_pseudogene(gene, feature):
                continue
            ncrnas.append(as_entry(record, gene, feature, context))

        for entry in helpers.generate_related(ncrnas):
            yield entry
