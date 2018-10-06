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


def domain_url(division):
    """Given E! division, returns E!/E! Genomes url."""
    if division == 'Ensembl':
        subdomain = 'ensembl.org'
    elif division == 'EnsemblPlants':
        subdomain = 'plants.ensembl.org'
    elif division == 'EnsemblMetazoa':
        subdomain = 'metazoa.ensembl.org'
    elif division == 'EnsemblBacteria':
        subdomain = 'bacteria.ensembl.org'
    elif division == 'EnsemblFungi':
        subdomain = 'fungi.ensembl.org'
    elif division == 'EnsemblProtists':
        subdomain = 'protists.ensembl.org'
    else:
        subdomain = None
    return subdomain


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


def parse(handle):
    reader = csv.DictReader(
        handle,
        fieldnames=('key', 'value'),
        delimiter='\t'
    )

    for entry in reader:
        assembly = {key: value for key, value in entry.items()}
        try:
            example_location = example_locations[assembly['species.url'].lower()]
        except KeyError:
            example_location = {'chromosome': None, 'start': None, 'end': None}

        url = assembly['species.url'].lower()
        is_mapped = int(url in BLAT_GENOMES)
        yield [
            assembly['assembly.default'],
            assembly['assembly.name'],
            assembly.get('assembly.accession', None),
            assembly.get('assembly.ucsc_alias', None),
            assembly.get('species.common_name', None),
            reconcile_taxids(assembly['species.taxonomy_id']),
            url,
            assembly['species.division'],
            domain_url(assembly['species.division']),
            example_location['chromosome'],
            example_location['start'],
            example_location['end'],
            is_mapped,
        ]


def write(handle, output):
    data = parse(handle)
    csv.writer(output).writerows(data)
