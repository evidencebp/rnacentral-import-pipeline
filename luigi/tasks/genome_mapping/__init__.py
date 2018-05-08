# -*- coding: utf-8 -*-

"""
Copyright [2009-2018] EMBL-European Bioinformatics Institute
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

from .genome_mapping_tasks import GetFasta
from .genome_mapping_tasks import CleanSplitFasta
from .genome_mapping_tasks import BlatJob
from .genome_mapping_tasks import ParseBlatOutput
from .genome_mapping_tasks import SpeciesBlatJobWrapper
from .genome_mapping_tasks import get_mapped_assemblies
from .genome_mapping_tasks import DownloadGenome
from .genome_mapping_tasks import GenerateOOCfile
from .update_ensembl_assembly import RetrieveEnsemblAssemblies
from .update_ensembl_assembly import RetrieveEnsemblGenomesAssemblies

from .pgload_exact_matches import GenomeMappingPGLoadExactMatches
from .pgload_inexact_matches import GenomeMappingPGLoadInexactMatches
from .pgload_ensembl_assembly import GenomeMappingPGLoadEnsemblAssembly
from .pgload_ensembl_assembly import GenomeMappingPGLoadEnsemblGenomesAssembly


class GenomeMappingPipelineWrapper(luigi.WrapperTask):
    """
    A wrapper task for the entire genome mapping pipeline.
    Genome download and blat searches are triggered in the
    GenomeMappingPGLoadInexactMatches task.
    """
    species = luigi.Parameter(default='')

    def requires(self):
        yield GenomeMappingPGLoadEnsemblAssembly()
        yield GenomeMappingPGLoadEnsemblGenomesAssembly()
        for assembly in get_mapped_assemblies():
            if self.species and assembly['species'] != self.species:
                continue
            yield GenomeMappingPGLoadInexactMatches(taxid=assembly['taxid'],
                                                    species=assembly['species'],
                                                    assembly_id=assembly['assembly_id'],
                                                    division=assembly['division'])

class ParseBlatOutputWrapper(luigi.WrapperTask):
    """
    A wrapper task for parsing all blat output into tsv files that can be
    loaded into the database.
    """
    species = luigi.Parameter(default='')

    def requires(self):
        for assembly in get_mapped_assemblies():
            if self.species and assembly['species'] != self.species:
                continue
            yield ParseBlatOutput(taxid=assembly['taxid'],
                                 species=assembly['species'],
                                 assembly_id=assembly['assembly_id'],
                                 division=assembly['division'])


class DownloadGenomes(luigi.WrapperTask):
    """
    A wrapper task for downloading genomes of all assemblies listed in the database.
    """
    species = luigi.Parameter(default='')

    def requires(self):
        for assembly in get_mapped_assemblies():
            if self.species and assembly['species'] != self.species:
                continue
            yield DownloadGenome(species=assembly['species'],
                                 division=assembly['division'])


class BlatWrapper(luigi.WrapperTask):
    """
    A wrapper task for launching blat jobs.
    """
    species = luigi.Parameter(default='')

    def requires(self):
        for assembly in get_mapped_assemblies():
            if self.species and assembly['species'] != self.species:
                continue
            yield SpeciesBlatJobWrapper(taxid=assembly['taxid'],
                                        species=assembly['species'],
                                        division=assembly['division'])
