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

import luigi

from tasks.config import export
from tasks.utils.files import atomic_output

from .data import Md5Data


class Md5Example(luigi.Task):
    def requires(self):
        return Md5Data()

    def output(self):
        return luigi.LocalTarget(export().md5('example.txt'))

    def data(self):
        count = export().md5_example_size
        with self.requires().output().open('r') as raw:
            return list(it.islice(raw, count))

    def run(self):
        with atomic_output(self.output()) as out:
            for line in self.data():
                out.write(line)
