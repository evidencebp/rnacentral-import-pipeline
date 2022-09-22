# -*- coding: utf-8 -*-

"""
Copyright [2009-2020] EMBL-European Bioinformatics Institute
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

import collections as coll
import csv
import logging
from pathlib import Path

import click

from rnacentral_pipeline import writers
from rnacentral_pipeline.databases.pdb import fetch, parser

LOGGER = logging.getLogger(__name__)


@click.group("pdb")
def cli():
    """
    Commands for dealing with the fetching PDB data.
    """
    pass


@cli.command("generate")
@click.option("--skip-references", default=False)
@click.argument(
    "output",
    default=".",
    type=click.Path(
        writable=True,
        dir_okay=True,
        file_okay=False,
    ),
)
@click.option(
    "--override-chains",
    default=None,
    type=click.File("r"),
)
def process_pdb(output, skip_references=False, override_chains=None):
    """
    This will fetch and parse all sequence data from PDBe to produce the csv
    files we import.
    """
    pdb_ids = set()
    if override_chains:
        for row in csv.reader(override_chains, delimiter="\t"):
            pdb_ids.add((row[0].lower(), row[1]))
    chain_info = fetch.rna_chains()
    references = {}
    try:
        if not skip_references:
            references = fetch.references(chain_info)
    except Exception:
        LOGGER.info("Failed to get extra references")

    entries = parser.parse(chain_info, references, pdb_ids)
    with writers.entry_writer(Path(output)) as writer:
        writer.write(entries)
