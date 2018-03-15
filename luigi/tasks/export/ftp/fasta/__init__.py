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

from tasks.utils.compress import GenericCompressTask

from .active import ActiveFastaExport
from .active import SpeciesSpecificFastaExport
from .inactive import InactiveFastaExport
from .nhmmer import NHmmerIncludedExport
from .nhmmer import NHmmerExcludedExport
from .readme import FastaReadme


class CompressExport(GenericCompressTask):
    """
    This will compress the files the generic FASTA export files.
    """

    def inputs(self):
        yield ActiveFastaExport()
        yield InactiveFastaExport()
        yield SpeciesSpecificFastaExport()

    def requires(self):
        for requirement in super(CompressExport, self).requires():
            yield requirement
        yield NHmmerExcludedExport()
        yield NHmmerIncludedExport()


class FastaExport(luigi.WrapperTask):
    """
    This is the main class to generate all FASTA file exports.
    """

    def requires(self):
        yield FastaReadme()
        yield NHmmerExport()
        yield CompressExport()


class NHmmerExport(luigi.WrapperTask):
    """
    This does the exports required for nhmmer.
    """

    def requires(self):
        yield NHmmerExcludedExport()
        yield NHmmerIncludedExport()
