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

from ..helpers import load_data

from rnacentral_pipeline.rnacentral.precompute.description import short


@pytest.mark.parametrize('rna_id,description,expected', [  # pylint: disable=no-member
    ('URS0000D50284_7240', 'Drosophila simulans () microRNA dsi-mir-988 precursor', 'microRNA dsi-mir-988 precursor'),
    ('URS0000795103_6239', 'Caenorhabditis elegans () microRNA cel-mir-8204 precursor', 'microRNA cel-mir-8204 precursor'),
    ('URS0000D5657E_7240', 'Drosophila simulans () microRNA dsi-mir-4966 precursor (dsi-mir-4966-3)', 'microRNA dsi-mir-4966 precursor (dsi-mir-4966-3)'),
])
def test_computes_correct_short_descriptions(rna_id, description, expected):
    data = load_data(rna_id)
    assert short.short_description(description, data) == expected