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

from tasks.config import export

from .compressed import CompressedRfamAnnotations
from .readme import RfamAnnotationsReadMe
from .examples import RfamAnnotationsExample


class ExportRfamAnnotaitons(luigi.WrapperTask):
    def requires(self):
        try:
            os.makedirs(export().rfam())
        except:
            pass

        yield CompressedRfamAnnotations()
        yield RfamAnnotationsReadMe()
        yield RfamAnnotationsExample()