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
from rnacentral_pipeline.writers import write_ontology_annotations as onto_writer

from rnacentral_pipeline.databases import rfam
from rnacentral_pipeline.databases.ena import parser as ena
from rnacentral_pipeline.databases.pdb import parser as pdb
from rnacentral_pipeline.databases.generic import parser as generic
from rnacentral_pipeline.databases.refseq import parser as refseq
from rnacentral_pipeline.databases.ensembl import parser as ensembl
from rnacentral_pipeline.databases.ensembl_genomes import plants as e_plants
from rnacentral_pipeline.databases.ensembl_genomes import fungi as e_fungi
from rnacentral_pipeline.databases.ensembl_genomes import metazoa as e_metazoa
from rnacentral_pipeline.databases.ensembl_genomes import protists as e_protists
from rnacentral_pipeline.databases.quickgo import parser as quickgo
from rnacentral_pipeline.databases.gtrnadb import parser as gtrnadb
from rnacentral_pipeline.databases.ncbi.gene import parser as ncbi_gene


@click.group('external', cls=ClickAliasedGroup)
def cli():
    """
    This is a group of commands for processing data from various databases into
    the CSV files that can be loaded by pgloader.
    """
    pass


@cli.command('json-schema', aliases=[
    '5srrnadb',
    'flybase',
    'lncbase',
    'lncbook',
    'lncipedia',
    'mirbase',
    'mirgenedb',
    'pombase',
    'snodb',
    'sgd',
    'tarbase',
    'zwd',
])
@click.argument('json_file', type=click.File('r'))
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
@click.argument('ensembl_file', type=click.File('r'))
@click.argument('family_file', type=click.Path(
    file_okay=True,
    dir_okay=False,
    readable=True,
))
@click.argument('gencode_gff', type=click.Path(
    file_okay=True,
    dir_okay=False,
    readable=True,
))
@click.argument('exclude', type=click.File('r'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_ensembl(ensembl_file, family_file, gencode_gff, exclude, output):
    """
    This will parse EMBL files from Ensembl to produce the expected CSV files.
    """
    write_entries(
        ensembl.parse, 
        output, 
        ensembl_file, 
        family_file, 
        gencode_gff,
        exclude,
    )


@cli.command('ensembl_plants')
@click.argument('ensembl_file', type=click.File('r'))
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


@cli.command('ensembl_fungi')
@click.argument('ensembl_file', type=click.File('r'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_ensembl_fungi(ensembl_file, output):
    write_entries(e_fungi.parse, output, ensembl_file)


@cli.command('ensembl_metazoa')
@click.argument('ensembl_file', type=click.File('r'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_ensembl_metazoa(ensembl_file, output):
    write_entries(e_metazoa.parse, output, ensembl_file)


@cli.command('ensembl_protists')
@click.argument('ensembl_file', type=click.File('r'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_ensembl_protists(ensembl_file, output):
    write_entries(e_protists.parse, output, ensembl_file)


@cli.command('pdb')
@click.argument('pdb_data', default='pdb.json', type=click.File('r'))
@click.argument('extra', default='pdb-extra.json', type=click.File('r'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_pdb(pdb_data, extra, output):
    """
    This will fetch and parse all sequence data from PDBe to produce the csv
    files we import.
    """
    write_entries(pdb.parse, output, pdb_data, extra)


@cli.command('ena')
@click.argument('ena_file', type=click.File('r'))
@click.argument('mapping_file', type=click.File('r'))
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
    write_entries(ena.parse_with_mapping_file, output, ena_file, mapping_file)


@cli.command('ncbi-gene')
@click.argument('data-file', type=click.File('r'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_ncbi_gene(data_file, output):
    write_entries(ncbi_gene.parse, output, data_file)


@cli.command('quickgo')
@click.argument('raw_data', type=click.File('r'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def ontologies_quickgo(raw_data, output):
    """
    This will process a quickgo file and output files into the given directory.
    """
    onto_writer(quickgo.parser, output, raw_data)


@cli.command('refseq')
@click.argument('refseq_file', type=click.File('r'))
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
@click.argument('rfam_file', type=click.File('r'))
@click.argument('mapping_file', type=click.File('r'))
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


@cli.command('gtrnadb')
@click.argument('data_file', type=click.File('r'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_gtrnadb(data_file, output):
    write_entries(gtrnadb.parse, output, data_file)


@cli.command('genecards')
@click.argument('data_file', type=click.File('r'))
@click.argument('known_sequences', type=click.File('rb'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_genecarrds(data_file, known_sequences, output):
    write_entries(genecards.parse, output, data_file, known_sequences)


@cli.command('malacards')
@click.argument('data_file', type=click.File('r'))
@click.argument('known_sequences', type=click.File('rb'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def process_malacards(data_file, known_sequences, output):
    write_entries(malacards.parse, output, data_file, known_sequences)
