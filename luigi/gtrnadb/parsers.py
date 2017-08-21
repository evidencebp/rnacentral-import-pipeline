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

from databases.data import Exon
from databases.data import Entry
from databases.data import SecondaryStructure

from gtrnadb.helpers import url
from gtrnadb.helpers import anticodon
from gtrnadb.helpers import note_data
from gtrnadb.helpers import chromosome
from gtrnadb.helpers import common_name
from gtrnadb.helpers import lineage
from gtrnadb.helpers import species
from gtrnadb.helpers import description
from gtrnadb.helpers import product
from gtrnadb.helpers import primary_id
from gtrnadb.helpers import dot_bracket
from gtrnadb.helpers import accession
from gtrnadb.helpers import parent_accession


def gtrnadb_secondary_structure(data):
    """
    Generate a secondary structure from the raw angle bracket string. This
    will transform it into a reasonable dot-bracket string and create a
    SecondaryStructure object.
    """
    return SecondaryStructure(dot_bracket=dot_bracket(data))


def gtrnadb_exons(locations):
    """
    This will create the Exons from the data provided by GtRNAdb.
    """

    exons = []
    for exon in locations['exons']:
        complement = None
        if exon['strand'] == '+':
            complement = False
        elif exon['strand'] == '-':
            complement = True
        else:
            raise ValueError("Invalid strand %s" % exon)

        exons.append(Exon(
            primary_start=int(exon['start']),
            primary_end=int(exon['stop']),
            complement=complement,
        ))
    return exons


def gtrnadb_entries(data):
    """
    Take an entry from GtRNAdb and produce the RNAcentrals that it
    represents. A single entry may represent more than one Entry because it
    may occur in more than one location. As we provide an accession for
    each location this ends up representing more than one RNAcentral Entry.
    """

    if data['metadata']['pseudogene']:
        return

    two_d = gtrnadb_secondary_structure(data)
    for location in data['genome_locations']:
        yield Entry(
            primary_id=primary_id(data, location),
            accession=accession(data, location),
            ncbi_tax_id=int(data['ncbi_tax_id']),
            database='GtRNAdb',
            sequence=data['sequence'],
            exons=gtrnadb_exons(location),
            rna_type='tRNA',
            url=url(data),
            note_data=note_data(data),
            secondary_structure=two_d,
            chromosome=chromosome(location),
            species=species(data),
            common_name=common_name(data),
            anticodon=anticodon(data),
            lineage=lineage(data),
            gene=data['gene'],
            optional_id=data['gene'],
            product=product(data),
            parent_accession=parent_accession(location),
            description=description(data),
            mol_type='genomic DNA',
            feature_location_start=1,
            feature_location_stop=len(data['sequence']),
            gene_synonyms=data.get('synonyms', []),
        )


def parse(filename):
    """
    This will parse a JSON file produced by GtRNAdb and yield the RNAcentral
    entries that it represents.
    """

    with open(filename, 'rb') as raw:
        data = json.load(raw)
        for datum in data:
            for entry in gtrnadb_entries(datum):
                yield entry
