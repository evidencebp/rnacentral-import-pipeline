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

import itertools as it

from Bio.UniProt.GOA import gpa_iterator as raw_parser

from . import data
from . import helpers


def as_annotation(record):
    """
    Turn a record into an annotation.
    """

    return data.GoTermAnnotation(
        rna_id=helpers.rna_id(record),
        qualifier=helpers.qualifier(record),
        term_id=helpers.go_id(record),
        evidence_code=record['ECO_Evidence_code'],
        extensions=helpers.extensions(record),
        assigned_by=helpers.assigned_by(record),
        publications=helpers.publications(record),
    )


def parser(handle):
    """
    Parse the given file to produce an iterable of GoTerm objects to import.
    """
    records = raw_parser(handle)
    records = it.ifilter(lambda r: r['DB'] == 'RNAcentral', records)
    return it.imap(as_annotation, records)
