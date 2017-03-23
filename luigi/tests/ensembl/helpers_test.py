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

import pytest

import unittest as ut

from Bio import SeqIO

from ensembl.helpers import (
    gene,
    locus_tag,
    notes,
    note_data,
    taxid,
    transcript,
    xref_data,
    is_gene
)


class HelpersTest(ut.TestCase):
    filename = 'data/Homo_sapiens.GRCh38.87.chromosome.12.dat'

    @classmethod
    def setUpClass(cls):
        cls.features = {}
        cls.record = SeqIO.read(cls.filename, 'embl')
        for feature in cls.record.features:
            gene_name = feature.qualifiers.get('gene', [None])[0]
            key = (feature.type, gene_name)
            cls.features[key] = feature

    def test_gets_the_taxid(self):
        assert taxid(self.record) == 9606

    def test_it_can_get_gene(self):
        assert gene(self.features['misc_RNA', 'ENSG00000256263.1']) == \
            'ENSG00000256263.1'

    def test_it_gets_transcript_id(self):
        assert transcript(self.features['misc_RNA', 'ENSG00000256263.1']) == \
            'ENST00000535849.1'

    def test_it_can_get_notes(self):
        assert notes(self.features['misc_RNA', 'ENSG00000120645.11']) == [
            "processed_transcript",
            "transcript_id=ENST00000544511.1",
        ]

        assert notes(self.features['gene', 'ENSG00000256948.1']) == []

    def test_it_can_get_the_locus_tag(self):
        assert locus_tag(self.features['gene', 'ENSG00000256948.1']) == \
            'RP11-598F7.3'

    def test_it_knows_if_something_is_a_gene(self):
        assert is_gene(self.features['gene', 'ENSG00000256948.1']) is True
        assert is_gene(self.features['misc_RNA', 'ENSG00000120645.11']) is \
            False

    def test_it_can_get_grouped_notes(self):
        feature = self.features['misc_RNA', 'ENSG00000120645.11']
        assert note_data(feature) == {'transcript_id': ['ENST00000544511.1']}
        feature = self.features['gene', 'ENSG00000249695.6']
        assert note_data(feature) == {}

    def test_it_can_get_grouped_xref_data(self):
        feature = self.features['misc_RNA', 'ENSG00000256948.1']
        assert xref_data(feature) == {
            "Vega_transcript": ["OTTHUMT00000397386"],
            "UCSC": ["uc058jnh.1"],
            "Clone_based_vega_transcript": ["RP11-598F7.3-001"],
            "OTTT": ["OTTHUMT00000397386"],
            "RNAcentral": ["URS000010A1F5"],
        }

    @pytest.mark.skip()
    def test_it_knows_if_something_is_ncrna(self):
        pass

    @pytest.mark.skip()
    def test_it_can_lookup_lineage(self):
        pass
