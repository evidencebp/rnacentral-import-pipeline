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

import csv
import itertools as it
import json
import operator as op

from rnacentral_pipeline import psql
from rnacentral_pipeline.rnacentral.ftp_export.coordinates.bed import \
    write_bed_text

from . import data, rrna


def load(handle):
    for entry in psql.json_handler(handle):
        yield data.UnboundLocation.build(entry)


def split_key(value: data.UnboundLocation):
    extent = value.extent
    return (extent.chromosome, extent.strand, value.insdc_rna_type)


def split(handle):
    entries = load(handle)
    for (key, locations) in it.groupby(entries, split_key):
        if key[-1] != "rRNA":
            continue

        yield list(locations)


def build(data):
    for group in data:
        genes = rrna.build(group)
        for gene in genes:
            yield gene


def write_genes(data, output):
    rows = it.chain.from_iterable(d.writeable() for d in data)
    writer = csv.writer(output)
    writer.writerows(rows)


def write_bed(data, output, extended=False):
    bed = it.chain.from_iterable(d.as_bed() for d in data)
    write_bed_text(bed, output, extended=extended)


def write(raw, output, as_bed):
    data = split(raw)
    data = build(data)
    if as_bed:
        write_bed(data, output)
    else:
        write_genes(data, output)
