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

import csv
import json
import itertools as it


UNCULTURED_TAXIDS = {
    155900,
    198431,
    415540,
    358574,
    81726,
}


def exclude_uncultured(annotation):
    """
    Detect if the annotation is from an uncultured organism and thus should be
    excluded.
    """
    return int(annotation['taxid']) not in UNCULTURED_TAXIDS


def parse(handle):
    data = it.imap(json.loads, handle)
    data = it.ifilter(exclude_uncultured, data)
    return data


def export(handle, output):
    """
    Write the Rfam based GO annotations to the given handle.
    """

    writer = csv.DictWriter(
        output,
        ['id', 'ontology_term_id', 'models'],
        extrasaction='ignore',
        delimiter='\t',
    )
    writer.writerows(parse(handle))