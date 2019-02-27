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

from rnacentral_pipeline.databases.crw import secondary_models as crw


@pytest.fixture()
def parsed():
    with open('data/crw/simple-data.tsv') as raw:
        return {i.model_id: i for i in crw.parse(raw)}


@pytest.mark.parametrize('filename,count', [
    ('data/crw/simple-data.tsv', 49),
])
def test_parses_whole_file(filename, count):
    with open(filename) as raw:
        assert len(list(crw.parse(raw))) == count


def test_can_build_correct_data(parsed):
    assert parsed['a.I1.m.A.aegerita.C2.SSU'] == crw.Info(
        model_id='a.I1.m.A.aegerita.C2.SSU',
        is_intronic=True,
        so_term='SO:0000587',
        taxid=5400,
        accessions=['U54637'],
        cell_location='Mitochondrion',
    )
