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

import luigi
from luigi.contrib.external_program import ExternalProgramTask

from .range import ExportJsonRange


class ValidateJsonRange(ExternalProgramTask):
    start = luigi.IntParameter()
    stop = luigi.IntParameter()
    schema = luigi.Parameter(default='schema/ensembl.json')

    def requires(self):
        return ExportJsonRange(start=self.start, stop=self.stop)

    def output(self):
        return []

    def program_args(self):
        return [
            'jsonschema',
            '-i',
            self.requires().output().fn,
            self.schema,
        ]