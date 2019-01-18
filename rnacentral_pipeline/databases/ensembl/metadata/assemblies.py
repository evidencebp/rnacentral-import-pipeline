# -*- coding: utf-8 -*-

"""
Copyright [2009-2018] EMBL-European Bioinformatics Institute
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

import csv
import json
import operator as op
import itertools as it

import attr
from attr.validators import optional
from attr.validators import instance_of as is_a

from . import databases as db

REJECTED_TAXIDS = {
    4932,
    5127,
}

BLAT_GENOMES = {
    'anopheles_gambiae',
    'arabidopsis_thaliana',
    'bombyx_mori',
    'caenorhabditis_elegans',
    'dictyostelium_discoideum',
    'drosophila_melanogaster',
    'homo_sapiens',
    'mus_musculus',
    'plasmodium_falciparum',
    'rattus_norvegicus'
    'saccharomyces_cerevisiae',
    'schizosaccharomyces_pombe',
}


def reconcile_taxids(taxid):
    """
    Sometimes Ensembl taxid and ENA/Expert Database taxid do not match,
    so to reconcile the differences, taxids in the ensembl_assembly table
    are overriden to match other data.
    """

    taxid = str(taxid)
    if taxid == '284812':  # Ensembl assembly for Schizosaccharomyces pombe
        return 4896  # Pombase and ENA xrefs for Schizosaccharomyces pombe
    return int(taxid)


def is_ignored_assembly(info):
    if info.taxid in REJECTED_TAXIDS:
        return True
    if info.taxid == 7227 and info.division != 'Ensembl':
        return True
    if info.taxid == 5762 and info.assembly_id == 'V1.0':
        return True
    if info.taxid == 6239 and info.division != 'Ensembl':
        return True
    if info.taxid == 8090 and info.ensembl_url != 'oryzias_latipes':
        return True
    return False


class InvalidDomain(Exception):
    """
    Raised when we cannot compute a URL for a domain.
    """
    pass


@attr.s()
class AssemblyExample(object):
    chromosome = attr.ib(validator=is_a(basestring))
    start = attr.ib(validator=is_a(int))
    end = attr.ib(validator=is_a(int))

    @classmethod
    def build(cls, raw, example_locations):
        key = raw['species.url'].lower()
        if key not in example_locations:
            return None

        example = example_locations[key]
        return cls(
            chromosome=str(example['chromosome']),
            start=example['start'],
            end=example['end'],
        )


@attr.s()
class AssemblyInfo(object):
    assembly_id = attr.ib(validator=is_a(basestring))
    assembly_full_name = attr.ib(validator=is_a(basestring))
    gca_accession = attr.ib(validator=optional(is_a(basestring)))
    assembly_ucsc = attr.ib(validator=optional(is_a(basestring)))
    common_name = attr.ib(validator=optional(is_a(basestring)))
    taxid = attr.ib(validator=is_a(int))
    ensembl_url = attr.ib(validator=is_a(basestring))
    division = attr.ib(validator=is_a(basestring))
    blat_mapping = attr.ib(validator=is_a(bool))
    example = attr.ib(validator=optional(is_a(AssemblyExample)))

    @classmethod
    def build(cls, raw, example_locations):
        url = raw['species.url'].lower()
        is_mapped = url in BLAT_GENOMES

        return cls(
            assembly_id=raw['assembly.default'],
            assembly_full_name=raw['assembly.name'],
            gca_accession=raw.get('assembly.accession', None),
            assembly_ucsc=raw.get('assembly.ucsc_alias', None),
            common_name=raw.get('species.common_name', None),
            taxid=reconcile_taxids(raw['species.taxonomy_id']),
            ensembl_url=url,
            division=raw['species.division'],
            blat_mapping=is_mapped,
            example=AssemblyExample.build(raw, example_locations),
        )

    @property
    def subdomain(self):
        """Given E! division, returns E!/E! Genomes url."""

        if self.division == 'Ensembl':
            return 'ensembl.org'
        if self.division == 'EnsemblPlants':
            return 'plants.ensembl.org'
        if self.division == 'EnsemblMetazoa':
            return 'metazoa.ensembl.org'
        if self.division == 'EnsemblBacteria':
            return 'bacteria.ensembl.org'
        if self.division == 'EnsemblFungi':
            return 'fungi.ensembl.org'
        if self.division == 'EnsemblProtists':
            return 'protists.ensembl.org'
        if self.division == 'EnsemblVertebrates':
            return 'ensembl.org'
        raise InvalidDomain(self.division)

    def writeable(self):
        chromosome = None
        start = None
        end = None
        if self.example:
            chromosome = self.example.chromosome
            start = self.example.start
            end = self.example.end

        return [
            self.assembly_id,
            self.assembly_full_name,
            self.gca_accession,
            self.assembly_ucsc,
            self.common_name,
            self.taxid,
            self.ensembl_url,
            self.division,
            self.subdomain,
            chromosome,
            start,
            end,
            int(self.blat_mapping),
        ]


def fetch(connections, query_handle, example_locations):
    results = db.run_queries_across_databases(connections, query_handle)
    for (_, rows) in results:
        raw = {r['meta_key']: r['meta_value'] for r in rows}
        if raw['species.division'] == 'EnsemblBacteria':
            continue
        info = AssemblyInfo.build(raw, example_locations)
        if is_ignored_assembly(info):
            continue
        yield info


def write(connections, query, example_file, output):
    """
    Parse the given input handle and write the readable data to the CSV.
    """

    examples = json.load(example_file)
    data = fetch(connections, query, examples)
    data = it.imap(op.methodcaller('writeable'), data)
    csv.writer(output).writerows(data)
