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

import attr
import pytest

from rnacentral_pipeline.databases import data as dat
from rnacentral_pipeline.databases.helpers import phylogeny as phy
from rnacentral_pipeline.databases.refseq import parser


@pytest.mark.parametrize('filename,count', [
    ('data/refseq/biomol_ncRNA_RNase_MRP_RNA.gbff', 4),
    ('data/refseq/mir-with-several-locations.gbff', 2),
    ('data/refseq/refseq_product.gbff', 2),
    ('data/refseq/related.gbff', 5),
    ('data/refseq/biomol_ncRNA_RNase_P_RNA.gbff', 9),
])
def test_can_parse_refseq_files(filename, count):
    with open(filename, 'r') as raw:
        assert len(list(parser.parse(raw))) == count


@pytest.mark.skip()
def test_extracts_correct_chromosome_if_several():
    with open('data/refseq/mir-with-several-locations.gbff', 'r') as raw:
        data = next(parser.parse(raw))
    assert data.chromosome == 'X'


def test_it_can_build_correct_entry():
    with open('data/refseq/biomol_ncRNA_RNase_MRP_RNA.gbff', 'rb') as raw:
        data = list(parser.parse(raw))

    assert len(data) == 4
    data = next(d for d in data if d.accession == 'NR_003051.3:1..277:ncRNA')
    data = attr.asdict(data)
    assert len(data['references']) == 10
    data['references'] = []

    assert data == attr.asdict(dat.Entry(
        primary_id='NR_003051',
        accession='NR_003051.3:1..277:ncRNA',
        ncbi_tax_id=9606,
        database='REFSEQ',
        sequence=(
            'GGTTCGTGCTGAAGGCCTGTATCCTAGGCTACACACTGAGGACTCTGTTCCTCCCCTTTC'
            'CGCCTAGGGGAAAGTCCCCGGACCTCGGGCAGAGAGTGCCACGTGCATACGCACGTAGAC'
            'ATTCCCCGCTTCCCACTCCAAAGTCCGCCAAGAAGCGTATCCCGCTGAGCGGCGTGGCGC'
            'GGGGGCGTCATCCGTCAGCTCCCTCTAGTTACGCAGGCAGTGCGTGTCCGCGCACCAACC'
            'ACACGGGGCTCATTCTCAGCGCGGCTGTAAAAAAAAA'
        ),
        regions=[],
        rna_type='RNase_MRP_RNA',
        url='https://www.ncbi.nlm.nih.gov/nuccore/NR_003051.3',
        seq_version='3',
        parent_accession='NR_003051',
        is_composite='N',
        description=(
            'Homo sapiens RNA component of mitochondrial RNA processing '
            'endoribonuclease (RMRP), RNase MRP RNA'
        ),
        xref_data={
            'GeneID': ['6023'],
            'HGNC': ['HGNC:10031'],
            'MIM': ['157660'],
        },
        note_data={},
        chromosome='9',
        species="Homo sapiens",
        common_name='human',
        lineage=(
            'Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; '
            'Euteleostomi; Mammalia; Eutheria; Euarchontoglires; '
            'Primates; Haplorrhini; Catarrhini; Hominidae; Homo; '
            'Homo sapiens'
        ),
        gene="RMRP",
        gene_synonyms=["CHH", "NME1", "RMRPR", "RRP2"],
        keywords='RefSeq',
        optional_id="GeneID:6023",
        product='RNA component of mitochondrial RNA processing endoribonuclease',
        mol_type="transcribed RNA",
    ))


def test_can_build_correct_entries_when_multiple_present():
    with open('data/refseq/mir-with-several-locations.gbff', 'r') as raw:
        data = [attr.asdict(e) for e in parser.parse(raw)]

    assert len(data) == 2
    assert len(data[0]['references']) == 2
    assert len(data[1]['references']) == 2
    assert data[0]['references'] == data[1]['references']

    data[0]['references'] = []
    data[1]['references'] = []

    assert data[0] == attr.asdict(dat.Entry(
        primary_id='NR_106737',
        accession='NR_106737.1:1..64:precursor_RNA',
        ncbi_tax_id=9606,
        database='REFSEQ',
        sequence=(
            'CCCCGGGCCCGGCGTTCCCTCCCCTTCCGTGCGCCAGTGGAGGCCGGGGTGGGGCGGGGCGGGG'
        ),
        regions=[],
        rna_type='precursor_RNA',
        url='https://www.ncbi.nlm.nih.gov/nuccore/NR_106737.1',
        seq_version='1',
        parent_accession='NR_106737',
        is_composite='N',
        description='Homo sapiens microRNA 6089 (MIR6089), precursor RNA',
        xref_data={
            'GeneID': ['102464837'],
            'HGNC': ['HGNC:50179'],
            'miRBase': ['MI0020366'],
        },
        note_data={},
        chromosome='X',
        species="Homo sapiens",
        common_name=u'human',
        lineage=(
            'Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; '
            'Euteleostomi; Mammalia; Eutheria; Euarchontoglires; '
            'Primates; Haplorrhini; Catarrhini; Hominidae; Homo; '
            'Homo sapiens'
        ),
        gene="MIR6089",
        gene_synonyms=[
            'hsa-mir-6089-1',
            'hsa-mir-6089-2',
            'MIR6089-1',
            'MIR6089-2',
        ],
        keywords='RefSeq',
        optional_id="GeneID:102464837",
        product='microRNA 6089',
        mol_type="transcribed RNA",
        related_sequences=[
            dat.RelatedSequence(
                sequence_id='NR_106737.1:39..62:ncRNA',
                relationship='mature_product',
            )
        ]
    ))

    assert data[1] == attr.asdict(dat.Entry(
        primary_id='NR_106737',
        accession='NR_106737.1:39..62:ncRNA',
        ncbi_tax_id=9606,
        database='REFSEQ',
        sequence='GGAGGCCGGGGTGGGGCGGGGCGG',
        regions=[],
        rna_type='miRNA',
        url='https://www.ncbi.nlm.nih.gov/nuccore/NR_106737.1',
        seq_version='1',
        parent_accession='NR_106737',
        is_composite='N',
        description='Homo sapiens microRNA 6089 (MIR6089), miRNA',
        xref_data={
            'GeneID': ['102464837'],
            'HGNC': ['HGNC:50179'],
            'miRBase': ['MI0020366', 'MIMAT0023714'],
        },
        note_data={},
        chromosome='X',
        species="Homo sapiens",
        common_name='human',
        lineage=(
            'Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; '
            'Euteleostomi; Mammalia; Eutheria; Euarchontoglires; '
            'Primates; Haplorrhini; Catarrhini; Hominidae; Homo; '
            'Homo sapiens'
        ),
        gene="MIR6089",
        gene_synonyms=[
            'hsa-mir-6089-1',
            'hsa-mir-6089-2',
            'MIR6089-1',
            'MIR6089-2',
        ],
        keywords='RefSeq',
        optional_id="GeneID:102464837",
        product='hsa-miR-6089',
        mol_type="transcribed RNA",
        related_sequences=[
            dat.RelatedSequence(
                sequence_id='NR_106737.1:1..64:precursor_RNA',
                relationship='precursor',
            )
        ]
    ))


def test_can_assign_related_sequences_for_mirnas():
    with open('data/refseq/related.gbff', 'r') as raw:
        data = [attr.asdict(e) for e in parser.parse(raw)]

    assert len(data) == 5
    assert len(data[0]['references']) == 4
    data[0]['references'] = []
    assert data[0] == attr.asdict(dat.Entry(
        primary_id='NR_000169',
        accession='NR_000169.2:1..98:precursor_RNA',
        ncbi_tax_id=6239,
        database='REFSEQ',
        sequence='TAGTAGACATTCTCCGATCTTTGGTGATTCAGCTTCAATGATTGGCTACAGGTTTCTTTCATAAAGCTAGGTTACCAAAGCTCGGCGTCTTGATCTAC',
        regions=[],
        rna_type='precursor_RNA',
        url='https://www.ncbi.nlm.nih.gov/nuccore/NR_000169.2',
        seq_version='2',
        parent_accession='NR_000169',
        is_composite='N',
        description='Caenorhabditis elegans pre-microRNA mir-79 (mir-79), precursor RNA',
        xref_data={
            'GeneID': ['259856']
        },
        note_data={},
        chromosome='I',
        species='Caenorhabditis elegans',
        lineage=phy.lineage(6239),
        gene="mir-79",
        gene_synonyms=[],
        keywords='RefSeq',
        optional_id="GeneID:259856",
        product="pre-microRNA mir-79",
        mol_type='transcribed RNA',
        project='PRJNA158',
        standard_name='C12C8.4',
        locus_tag='CELE_C12C8.4',
        related_sequences=[
            dat.RelatedSequence(
                sequence_id='NR_000169.2:19..41:ncRNA',
                relationship='mature_product',
            ),
            dat.RelatedSequence(
                sequence_id='NR_000169.2:61..82:ncRNA',
                relationship='mature_product',
            ),
        ]
    ))

    assert data[1]['related_sequences'] == [attr.asdict(dat.RelatedSequence(
        sequence_id='NR_000169.2:1..98:precursor_RNA',
        relationship='precursor'
    ))]

    assert data[1]['related_sequences'] == [attr.asdict(dat.RelatedSequence(
        sequence_id='NR_000169.2:1..98:precursor_RNA',
        relationship='precursor',
    ))]


def test_can_assign_isoform_to_rnase_p():
    with open('data/refseq/biomol_ncRNA_RNase_P_RNA.gbff', 'r') as raw:
        data = [attr.asdict(e) for e in parser.parse(raw)]

    entry = next(d for d in data if d['accession'] == 'NR_002092.1:1..299:ncRNA')
    entry['sequence'] = ''
    entry['references'] = []
    assert entry == attr.asdict(dat.Entry(
        primary_id='NR_002092',
        accession='NR_002092.1:1..299:ncRNA',
        ncbi_tax_id=7227,
        database='REFSEQ',
        sequence='',
        regions=[],
        rna_type="RNase_P_RNA",
        url='https://www.ncbi.nlm.nih.gov/nuccore/NR_002092.1',
        seq_version='1',
        parent_accession='NR_002092',
        is_composite='N',
        description='Drosophila melanogaster ribonuclease P RNA (RNaseP:RNA), RNase P RNA',
        xref_data={
            'GeneID': ['3772418'],
            'FLYBASE': ['FBgn0046696', 'FBtr0085775'],
        },
        note_data={},
        chromosome='3R',
        species='Drosophila melanogaster',
        common_name='fruit fly',
        lineage=(
           'Eukaryota; Metazoa; Ecdysozoa; Arthropoda; '
           'Hexapoda; Insecta; Pterygota; Neoptera; Holometabola; '
           'Diptera; Brachycera; Muscomorpha; Ephydroidea; '
           'Drosophilidae; Drosophila; Sophophora; Drosophila melanogaster'
        ),
        gene="RNaseP:RNA",
        gene_synonyms=[
            "chr3R:27043287..27043402",
            "CR32868",
            r"Dmel\CR32868",
            "P RNA",
            "RNase P RNA",
            "RNAseP",
            "RPR RNA",
        ],
        keywords='RefSeq',
        optional_id="GeneID:3772418",
        product="ribonuclease P RNA",
        mol_type="transcribed RNA",
        project='PRJNA164',
        locus_tag="Dmel_CR32868",
        related_sequences=[
            dat.RelatedSequence(
                sequence_id='NR_133496.1:1..295:ncRNA',
                relationship='isoform',
            ),
        ]
    ))
