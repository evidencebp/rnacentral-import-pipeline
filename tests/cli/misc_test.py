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

import pytest
from click.testing import CliRunner

from rnacentral_pipeline.cli import misc


@pytest.mark.cli
@pytest.mark.parametrize(
    "filename,exit_code",
    [
        ("data/pgloader/failed.txt", 1),
        ("data/pgloader/success.txt", 0),
    ],
)
def test_can_validate_pgloader_file(filename, exit_code):
    runner = CliRunner()
    result = runner.invoke(misc.validate_pgloader, [filename])
    assert result.exit_code == exit_code, result.output
