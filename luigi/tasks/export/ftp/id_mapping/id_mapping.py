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

import luigi

from tasks.config import db
from tasks.config import export
from tasks.utils.files import atomic_output

from rnacentral.export.ftp import id_mapping


class IdMapping(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            export().id_mapping('id_mapping.tsv.gz'),
            format=luigi.format.Gzip,
        )

    def run(self):
        with atomic_output(self.output()) as out:
            writer = csv.writer(out, delimiter='\t')
            writer.writerows(id_mapping.complete(db()))