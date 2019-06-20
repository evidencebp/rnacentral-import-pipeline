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

import operator as op
import itertools as it

from Bio import SeqIO

from rnacentral_pipeline.databases.helpers import embl
from rnacentral_pipeline.databases.ensembl import helpers as ensembl

from . import helpers


def ncrnas(context, handle):
    for record in SeqIO.parse(handle, 'embl'):
        current_gene = None
        for feature in record.features:
            if feature.type == 'source':
                continue

            if embl.is_gene(feature):
                current_gene = feature
                continue

            if helpers.is_pseudogene(current_gene, feature):
                continue

            if not helpers.is_ncrna(feature):
                continue

            yield helpers.as_entry(context, record, current_gene, feature)


def parse(context, handle):
    data = ncrnas(context, handle)
    grouped = it.groupby(data, op.attrgetter('gene'))
    for gene, related in grouped:
        for entry in ensembl.generate_related(related):
            yield entry
