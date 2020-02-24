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

import re
import typing as ty

from pathlib import Path

from rnacentral_pipeline.rnacentral.traveler import data


def paths(directory: Path):
    model_pattern = re.compile('^RF\d+$')
    for model_directory in directory.glob('RF*'):
        if not re.match(model_pattern, model_directory.name):
            continue

        model_id = model_directory.stem
        for path in model_directory.glob('*.fasta'):
            yield data.TravelerPaths(path.stem, model_id, data.Source.rfam, model_directory)