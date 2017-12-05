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

import os

import luigi

from .active import ActiveFastaExport
from .active import SpeciesSpecificFastaExport
from .inactive import InactiveFastaExport
from .nhmmer import NHmmerDBExport
from .nhmmer import NHmmerExcludedExport


class CompressExport(luigi.Task):

    def requires(self):
        yield ActiveFastaExport()
        yield InactiveFastaExport()
        yield SpeciesSpecificFastaExport()
        yield NHmmerExcludedExport()
        yield NHmmerDBExport()

    def output(self):
        for requirement in self.requires():
            yield luigi.LocalTarget(requirement.output().fn + '.gz')

    def run(self):
        for requirement in self.requires():
            os.system('gzip %s' % requirement.output().fn)
