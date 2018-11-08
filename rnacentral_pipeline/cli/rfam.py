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

from rnacentral_pipeline.databases import rfam


@click.group('rfam')
def cli():
    """
    Commands with processing the Rfam metadata.
    """
    pass


@cli.command('families')
@click.argument('filename', default='-', type=click.File('rb'))
@click.argument('output', default='rfam-families.csv', type=click.File('wb'))
def rfam_group_families(filename, output):
    rfam.families.from_file(filename, output)


@cli.command('clans')
@click.argument('filename', default='-', type=click.File('rb'))
@click.argument('output', default='rfam-clans.csv', type=click.File('wb'))
def rfam_group_clans(filename, output):
    rfam.clans.from_file(filename, output)


@cli.command('ontology-terms')
@click.argument('filename', default='-', type=click.File('rb'))
@click.argument('output', default='.', type=click.Path(
    writable=True,
    dir_okay=True,
    file_okay=False,
))
def ontologies_rfam_terms(filename, output):
    rfam.cross_references.from_file(filename, output)
