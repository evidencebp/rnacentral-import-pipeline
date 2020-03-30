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

from rnacentral_pipeline import psql


def access_id(entry):
    return entry['id']


def append_taxid(taxid):
    def fn(entry):
        urs = access_id(entry)
        return f"{urs}_{taxid}"
    return fn


def parse(handle, id_generator, extra_fields=[]):
    for entry in psql.json_handler(handle):
        yield [id_generator(entry)] + extra_fields


def parse_rfam_version(handle):
    for line in handle:
        if line.startswith('Release'):
            parts = line.split(' ')
            return parts[1].strip()
    raise ValueError("Could not find version in file")


def write(handle, id_generator, output, extra_fields=[]):
    writer = csv.writer(output)
    writer.writerows(parse(handle, id_generator, extra_fields=extra_fields))


def genome_mapping(handle, assembly_id, output):
    write(handle, access_id, output, extra_fields=[assembly_id])


def qa(handle, name, version_file, output):
    if name == 'rfam':
        version = parse_rfam_version(version_file)
    else:
        raise ValueError(f"Unknown QA type: {name}")
    write(handle, access_id, output, extra_fields=[name, version])


def traveler(handle, output):
    write(handle, access_id, output)
