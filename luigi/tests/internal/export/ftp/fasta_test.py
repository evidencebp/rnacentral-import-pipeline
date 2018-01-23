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

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from internal.export.ftp import fasta
from internal.psql import PsqlWrapper

from tasks.config import db

from tests.tasks.helpers import count


@pytest.mark.parametrize('sequence,accepted', [
    ('', False),
    ('A', True),
    ('A-', False),
    ('ABCDGHKMNRSTVWXYU', True),
    ('GCGGAUUUAGCUCAGUUGGGAGAGCGCCAGACUGAAGAUCUGGAGGUCCUGUGUUCGAUCCACAGAAUUCGCACCAF', False),
    ('GCCCGGAUAGCUCAGUCGGUAGAGCAGGGGAUUGAAAAUCCCCGUGUCCUUGGUUCGAUUCCGAGUCCGGGCACCAF', False),
    ('GCGGAUUUAGCUCAGUUGGGAGAGCGCCAGACUGAAGAUCUGGAGGUCCUGUGUUCGAUCCACAGAAUUCGCACCAFC', False),
    ('AUUIGAAAUC', False),
    ('CGGUGAIAAGGG', False),
    ('UUCCUCGUGGCCCAAUGGUCACGGCGUCUGGCUICGAACCAGAAGAUUCCAGGUUCAAGUCCUGGCGGGGAAGCCA', False),
    ('GGCUICGAACC', False),
    ('AUUIGAAAUCU', False),
    ('CUCGGCUICGAACCGAG', False),
    ('CUCGGXUICGAACCGAG', False),
])
def test_can_classify_sequences_for_nhmmer(sequence, accepted):
    record = SeqRecord(Seq(sequence))
    assert fasta.is_valid_nhmmer_record(record) is accepted


def test_can_produce_records_from_a_query():
    sql = "select upi as id, md5 as description, 'AAAA' as sequence from rna order by id desc limit 3"
    psql = PsqlWrapper(db())
    lines = [fasta.as_record(l) for l in psql.copy_to_iterable(sql)]
    # Biopython doesn't implement SeqRecord.__eq__, ugh
    assert len(lines) == 3
    assert lines[0].id == 'URS0000C8E9EF'
    assert lines[0].description == 'fc30780b063695720cc37a9ce1968b7a'
    assert lines[0].seq == Seq('AAAA')

    assert lines[1].id == 'URS0000C8E9EE'
    assert lines[1].description == 'f98993c13f10b65603df026553964f5e'
    assert lines[1].seq == Seq('AAAA')

    assert lines[2].id == 'URS0000C8E9ED'
    assert lines[2].description == 'ebad5a2c948b840158b6684319a826e3'
    assert lines[2].seq == Seq('AAAA')


@pytest.mark.slowtest
def test_active_sql_produces_correct_counts():
    assert count(fasta.ACTIVE_SQL) == 11075136


@pytest.mark.slowtest
def test_active_produces_correct_number_of_records():
    assert sum(1 for _ in fasta.active(db())) == 11075136


@pytest.mark.slowtest
def test_active_has_correct_first_record():
    data = next(fasta.active(db()))
    assert data.id == 'URS0000000001'
    assert data.description == 'environmental samples uncultured bacterium rRNA'
    assert data.seq == Seq('AUUGAACGCUGGCGGCAGGCCUAACACAUGCAAGUCGAGCGGUAGAGAGAAGCUUGCUUCUCUUGAGAGCGGCGGACGGGUGAGUAAUGCCUAGGAAUCUGCCUGGUAGUGGGGGAUAACGCUCGGAAACGGACGCUAAUACCGCAUACGUCCUACGGGAGAAAGCAGGGGACCUUCGGGCCUUGCGCUAUCAGAUGAGC')


@pytest.mark.slowtest
def test_species_sql_produces_correct_counts():
    assert count(fasta.ACITVE_SPECIES_SQL) == 13729588


@pytest.mark.slowtest
def test_species_produces_correct_number_of_records():
    assert sum(1 for _ in fasta.species(db())) == 13729588


@pytest.mark.slowtest
def test_species_has_correct_first_record():
    data = next(fasta.species(db()))
    assert data.id == 'URS000050A1B4_77133'
    assert data.description == 'uncultured bacterium partial 16S ribosomal RNA'
    assert data.seq == Seq('TGAGGAATATTGGTCAATGGGCGAGAGCCTGAAACCAGCCAAGTAGCGTGAAGGAAGACTGCCCTATGGGTTGTAAACTTCTTTTATAAGGGAATAAAGAGCGCCACGTGTGGTGTGTTGTATGTACCTTATGAATAAGCATCGGCTAATTCCGTGCC')


@pytest.mark.slowtest
def test_inactive_sql_produces_correct_counts():
    assert count(fasta.INACTIVE_SQL) == 2079637


@pytest.mark.slowtest
def test_inactive_produces_correct_number_of_records():
    assert sum(1 for _ in fasta.inactive(db())) == 2079637


@pytest.mark.slowtest
def test_inactive_has_correct_first_record():
    data = next(fasta.inactive(db()))
    assert data.id == 'URS00006E9C09'
    assert data.description == 'Saccoglossus kowalevskii rRNA'
    assert data.seq == Seq('GCCTACTGCCAAACCATTGCAAAATACACCAGTTCTCATCCGATCACTGAAGTTAAGCTGCATCGGGCGTGGTTAGTACTTGCATGGGAGACGGGTAGGGAATACCACGTGCAGTAGGCT')


@pytest.mark.slowtest
def test_produces_correct_example_records():
    data = list(fasta.example(db()))
    assert len(data) == 10

    assert data[0].id == 'URS0000000001'
    assert data[0].description == 'Uncultured bacterium partial 16S ribosomal RNA'
    assert data[0].seq == Seq('AUUGAACGCUGGCGGCAGGCCUAACACAUGCAAGUCGAGCGGUAGAGAGAAGCUUGCUUCUCUUGAGAGCGGCGGACGGGUGAGUAAUGCCUAGGAAUCUGCCUGGUAGUGGGGGAUAACGCUCGGAAACGGACGCUAAUACCGCAUACGUCCUACGGGAGAAAGCAGGGGACCUUCGGGCCUUGCGCUAUCAGAUGAGC')

    assert data[1].id == 'URS0000000003'
    assert data[1].description == 'environmental samples uncultured bacterium rrn'
    assert data[1].seq == Seq('GUAUGCAACUUACCUUUUACUAGAGAAUAGCCAAGAGAAAUUUUGAUUAAUGCUCUAUGUUCUUAUUUACUCGCAUGAGUAAAUAAGCAAAGCUCCGGCGGUAAAAGAUGGGCAUGCGUCCUAUUAGCUUGUAGGUGAGGUAAUGGCUCACCUAAGCUCCGAUAGGUAGGGGUCCUGAGAGGGAGAUCCCCCACACUGGUACUGAGACACGGACCAGACUUCUACGGAAGGCAGCAGUAAGGAAUAUUGGACAAUGGAGGCAACUCUGAUCCAGCCAUGCCGCGUGAAGGAAGACGGCCUUAUGGGUUGUAAACUUCUUUUAUACAGGAAGAAACCUUUCCACGUGUGGAAAGCUGACGGUAC')

    assert data[2].id == 'URS0000000004'
    assert data[2].description == 'environmental samples uncultured bacterium rrn'
    assert data[2].seq == Seq('CACGCAGGCGGUUCUGCGCGUUUCGAGUGACAGCGGGCGGCUUACCUGCCCGAGUAUUCGAAAGACGGUAGGACUUGAGGGCCAGAGAGGGACACGGAAUUCCGGGUGGAGUGGUGAAAUGCGUAGAGAUCCGGAGGAACACCGAAGGCGAAGGCAGUGUCCUGGCUGGUGACUGACGCUGAGGUGCGAAAGCCGAGGGGAGCGAACGGGAUUAGAUACCCCGGUAGUCCUGGCCGUAAACGAUGACCACCAGGUGUGGGAGGUAUCGACCCCUUCGUGCCGGAGUCAACACACUAAGUGGUCCGCCUGGGGAUACGGUCGCAAGAUUAAAA')

    assert data[3].id == 'URS0000000005'
    assert data[3].description == 'environmental samples uncultured bacterium rrn'
    assert data[3].seq == Seq('AGAGUUUGAUCCUGGCUCAGAAUGAACGCUGGCGGCGUGCCUUACACAUGCAAGUCGAGCGAGGCGCGGGGGCAACCCCGCAGUCGAGCGGCGAACGGGUGAGUAACACGUGGAUAACCUGCCCUGAGGCGUGGAACAACCAGGGGAAACUCUGGCUAAUACCGCAUGAUACCGAGAGGUCAAAGGGGGCUCGCAAGGGCUCUCGCCACAGGAGGGGUCCGCGUCCGAUUAGCUAGUUGGUAGGGUAAUGGCCUACCAAGGCGACGAUCGGUAGCCGGCCUGAGAGGGUGAUCGGCCACACUGGAACUGAGACACGGUCCAGACUCCUACGGGAGGCAGCAGUGGGGAAUUUUGCGCAAUGGGCUAACGCCUGACGCAGCAACGCCGCGUGGAGGAUGAAGGUCUUUGGAUUGUAAACUCCUGUCAGCAGGGAAAAAGCGAAUUGGCCUAAUACGCCAGUGAGUUGAUUGUACCUGCAGAGGAAGCCC')

    assert data[4].id == 'URS0000000006'
    assert data[4].description == 'Bathippus korei partial 16S ribosomal RNA'
    assert data[4].seq == Seq('UUAGUAGUAAAGUCUGCUCCAUGAAUACUUAAAUAGCCGCAAUUCGUGCUAAGGUAGCAUAAUCAUUUGUCUUUUAAAUGAGGACUAGAACAAAAGAUUUAACAUUUUAAAUUAUUUAUUUAAAUUAAUUAUUUAAAUUUUCUUAAGCGUAAAAAGACACUUAUUAAAAAGAAAGACGACAAGACCCUAUCGAACUUAACUCAAGUUUAACUGGGGUAGUUAAUUAAUUAUUAUUUUAAUAUACUAUAACUACUAAUUAUCUAAUUAAUUAAUAAUCCAGUUACCGUAGGGAUAACAGCGCAAUUAAAUUUUAAAGUACUUAUUUAAAAAAUAGAUUACGACCUCGAUGUUGAAUUAAUAACCUAUUUGAAGCAAAUUUCAAAAAAGGAAGUCUGUUCGACUUUUAAAAAAUUACAUGAUUUGAGUUCAGACCGGUAUAAGCCAGGUCGGUUUCAAUCUUCUAAAAACUCUUUUACAGUACGAAAGGACCUAAAAAUAUAAUUUAAUUAUUUAUAUUGGCAGAAAAAUGCAUUAGAAUUAGAAUCUAAUAAAACUUUU')
