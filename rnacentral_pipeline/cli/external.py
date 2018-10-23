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


import click
from click_aliases import ClickAliasedGroup

from rnacentral_pipeline.writers import write_entries

from rnacentral_pipeline.databases import rfam
from rnacentral_pipeline.databases.ena import parser as ena
from rnacentral_pipeline.databases.pdb import parser as pdb
from rnacentral_pipeline.databases.generic import parser as generic
from rnacentral_pipeline.databases.refseq import parser as refseq
from rnacentral_pipeline.databases.ensembl import parser as ensembl
from rnacentral_pipeline.databases.ensembl_plants import parser as e_plants


@click.group('external', cls=ClickAliasedGroup)
def cli():
    """
    This is a group of commands for processing data from various databases into
    the CSV files that can be loaded by pgloader.
    """
    pass


@cli.command('json-schema', aliases=[
    'flybase',
    'lncbase',
    'lncipedia',
    'mirbase',
    'pombase',
    'tarbase',
    'zwd',
])
@click.argument('json_file', type=click.File('rb'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_json_schema(json_file, output):
    """
    This parses our JSON schema files to produce the importable CSV files.
    """
    write_entries(generic.parse, output, json_file)


@cli.command('ensembl')
@click.argument('ensembl_file', type=click.File('rb'))
@click.argument('family_file', type=click.Path(
    file_okay=True,
    dir_okay=False,
    readable=True,
))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_ensembl(ensembl_file, family_file, output):
    """
    This will parse EMBL files from Ensembl to produce the expected CSV files.
    """
    write_entries(ensembl.parse, output, ensembl_file, family_file)


@cli.command('ensembl_plants')
@click.argument('ensembl_file', type=click.File('rb'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_ensembl_plants(ensembl_file, output):
    """
    This will process the Ensembl Plant data to produce files for import. The
    files should be in the EMBL format as provided by EnsemblPlants.
    """
    write_entries(e_plants.parse, output, ensembl_file)


@cli.command('gencode')
@click.argument('gencode_gff', type=click.File('rb'))
@click.argument('ensembl_file', type=click.File('rb'))
@click.argument('family_file', type=click.Path(
    file_okay=True,
    dir_okay=False,
    readable=True,
))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_gencode(gencode_gff, ensembl_file, family_file, output):
    """
    This will parse EMBL files from Ensembl to produce the expected CSV files.
    """
    # gencode.from_file(gencode_gff, ensembl_file, family_file, output)
    pass


@cli.command('pdb')
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_pdb(output):
    """
    This will fetch and parse all sequence data from PDBe to produce the csv
    files we import.
    """
    write_entries(pdb.entries, output)


@cli.command('ena')
@click.argument('ena_file', type=click.File('rb'))
@click.argument('mapping_file', type=click.File('rb'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_ena(ena_file, mapping_file, output):
    """
    Process ENA EMBL formatted files into CSV to import. The additional mapping
    file is a file containing all TPA data we are using from ENA.
    """
    write_entries(ena.parse, output, ena_file, mapping_file)


@cli.command('refseq')
@click.argument('refseq_file', type=click.File('rb'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_refseq(refseq_file, output):
    """
    This will parse GenBank files from refseq to produce the expected CSV files.
    """
    write_entries(refseq.parse, output, refseq_file)


@cli.command('rfam')
@click.argument('rfam_file', type=click.File('rb'))
@click.argument('mapping_file', type=click.File('rb'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_rfam(rfam_file, mapping_file, output):
    """
    Process Rfam's JSON format into the files to import.
    """
    write_entries(rfam.parser.parse, output, rfam_file, mapping_file)