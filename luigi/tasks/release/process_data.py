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

from tasks.ena import Ena
from tasks.ensembl.ensembl import Ensembl
from tasks.pdb import Pdb
from tasks.rfam import RfamSequences
from tasks.rfam import RfamFamilies
from tasks.rgd import Rgd


class ProcessData(luigi.WrapperTask):  # pylint: disable=R0904
    """
    This will generate the CSV's to import for all the databases we update each
    release.
    """

    def requires(self):
        yield Ena()
        yield Ensembl()
        yield RfamSequences()
        yield RfamFamilies()
        yield Pdb()
        yield Rgd()