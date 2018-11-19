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

from rnacentral_pipeline.rnacentral import genome_mapping


@click.group('genome-mapping')
def cli():
    """
    This group of commands deals with figuring out what data to map as well as
    parsing the result into a format for loading.
    """
    pass


@cli.command('select-hits')
@click.argument('hits', default='-', type=click.File('r'))
@click.argument('output', default='-', type=click.File('w'))
def mappable_species(hits, output):
    genome_mapping.write_selected(hits, output)
