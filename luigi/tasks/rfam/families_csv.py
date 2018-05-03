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

import operator as op

import luigi

from databases.rfam.families import parse

from tasks.config import rfam

from tasks.utils.fetch import FetchTask
from tasks.utils.writers import CsvOutput


class RfamFamiliesCSV(luigi.Task):
    headers = [
        'id',
        'short_name',
        'long_name',
        'description',
        'clan_id',
        'seed_count',
        'full_count',
        'length',
        'domain',
        'is_suppressed',
        'rna_type',
        'rfam_rna_type',
    ]

    def requires(self):
        conf = rfam()
        return FetchTask(
            remote_path=conf.query('families.sql'),
            local_path=conf.raw('clans.tsv'),
        )

    def output(self):
        conf = rfam()
        return CsvOutput(
            conf.families,
            self.headers,
            op.methodcaller('writeable'),
        )

    def run(self):
        with self.requires().output.open('r') as raw:
            self.output().populate(parse(raw))
