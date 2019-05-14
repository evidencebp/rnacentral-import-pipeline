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
import attr

from rnacentral_pipeline.databases import data as dat

from .helpers import parse_with_family, entries_for, entry_for, has_entry_for


@pytest.fixture(scope='module')  # pylint: disable=no-member
def human_12():
    return parse_with_family('data/ensembl/Homo_sapiens.GRCh38.chromosome.12.dat',
                             gencode_file='data/gencode/human-transcripts.gff3')


@pytest.fixture(scope='module')  # pylint: disable=no-member
def human_x():
    return parse_with_family('data/ensembl/Homo_sapiens.GRCh38.chromosome.X.dat')


@pytest.fixture(scope='module')  # pylint: disable=no-member
def macaca():
    return parse_with_family('data/ensembl/Macaca_mulatta.Mmul_8.0.1.chromosome.1.dat',
                             gencode_file='data/gencode/human-transcripts.gff3')


@pytest.fixture(scope='module')  # pylint: disable=no-member
def mouse_3():
    return parse_with_family('data/ensembl/Mus_musculus.GRCm38.chromosome.3.dat')


def test_it_sets_primary_id_to_versionless_transcript_id(human_12):
    assert entry_for(human_12, 'ENST00000516089.1').primary_id == \
        'ENST00000516089'


def test_it_generates_correct_seq_version(human_12):
    assert entry_for(human_12, 'ENST00000516089.1').seq_version == '1'


def test_sets_optional_id_to_gene_id(human_12):
    assert entry_for(human_12, 'ENST00000516089.1').optional_id == \
        "ENSG00000251898.1"


def test_it_gets_gene_id_to_locus(human_12):
    assert entry_for(human_12, 'ENST00000516089.1').gene == 'SCARNA11'


def test_it_gets_the_locus_tag(human_12):
    assert entry_for(human_12, 'ENST00000516089.1').locus_tag == 'SCARNA11'


def test_it_sets_rna_type_to_snRNA(human_12):
    assert entry_for(human_12, 'ENST00000516089.1').rna_type == 'snoRNA'
    assert entry_for(human_12, 'ENST00000540226.1').rna_type == 'antisense_RNA'


def test_it_sets_product_to_snaRNA(human_12):
    assert entry_for(human_12, "ENST00000516089.1").product == 'scaRNA'
    assert entry_for(human_12, "ENST00000516089.1").rna_type == 'snoRNA'


def test_it_sets_accession_to_transcript_id(human_12):
    assert entry_for(human_12, 'ENST00000540868.1').accession == \
        'ENST00000540868.1'


def test_it_does_not_create_entries_for_pseudogenes(human_12):
    entries = {e.optional_id for e in human_12}
    assert 'ENSG00000252079.1' not in entries


def test_it_normalizes_lineage_to_standard_one(human_12):
    assert entry_for(human_12, 'ENST00000540868.1').lineage == (
        "Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; "
        "Euteleostomi; Mammalia; Eutheria; Euarchontoglires; Primates; "
        "Haplorrhini; Catarrhini; Hominidae; Homo; Homo sapiens"
    )


def test_calls_lincRNA_lncRNA(human_12):
    assert entry_for(human_12, 'ENST00000538041.1').rna_type == 'lncRNA'


def test_uses_gene_description_if_possible(human_12):
    assert entry_for(human_12, 'ENST00000538041.1').description == \
        "Homo sapiens (human) long intergenic non-protein coding RNA 1486"


def test_description_strips_source(human_12):
    assert entry_for(human_12, 'ENST00000516089.1').description == \
        "Homo sapiens (human) small Cajal body-specific RNA 11"


def test_generated_description_includes_locus(human_12):
    assert entry_for(human_12, 'ENST00000501075.2').description == \
        "Homo sapiens (human) novel transcript, antisense to CHD4"


def test_can_correct_rfam_name_to_type(human_12):
    assert entry_for(human_12, 'ENST00000620330.1').rna_type == 'SRP_RNA'


def test_it_gets_simple_locations(human_12):
    assert entry_for(human_12, 'ENST00000546223.1').regions == [
        dat.SequenceRegion(
            chromosome='12',
            strand=-1,
            exons=[
                dat.Exon(start=37773, stop=38102),
                dat.Exon(start=36661, stop=37529),
            ],
            assembly_id='GRCh38',
            coordinate_system=dat.CoordinateSystem.one_based(),
        )
    ]


def test_can_get_joined_locations(human_12):
    assert entry_for(human_12, 'ENST00000543036.1').regions == [
        dat.SequenceRegion(
            chromosome='12',
            strand=1,
            exons=[
                dat.Exon(start=3319441, stop=3319726),
                dat.Exon(start=3323349, stop=3323452),
                dat.Exon(start=3325090, stop=3325340),
            ],
            assembly_id='GRCh38',
            coordinate_system=dat.CoordinateSystem.one_based(),
        )
    ]


def test_it_gets_cross_references(human_12):
    assert entry_for(human_12, 'ENST00000504074.1').xref_data == {
        "UCSC": ["ENST00000504074.1"],
        "RNAcentral": ["URS000042090E"],
        "HGNC_trans_name": ['FAM138D-201'],
        "RefSeq_ncRNA": ['NR_026823'],
    }


def test_it_uses_correct_antisense_type(human_12):
    assert entry_for(human_12, 'ENST00000605233.2').rna_type == 'antisense_RNA'


def test_it_does_not_import_suprressed_rfam_families(human_12):
    assert not entries_for(human_12, 'ENST00000611210.1')


def test_it_builds_correct_entries(human_12):
    val = attr.asdict(entry_for(human_12, 'ENST00000620330.1'))
    del val['sequence']
    ans = attr.asdict(dat.Entry(
        primary_id='ENST00000620330',
        accession='ENST00000620330.1',
        ncbi_tax_id=9606,
        database='ENSEMBL',
        sequence='A',
        regions=[
            dat.SequenceRegion(
                chromosome='12',
                strand=1,
                exons=[dat.Exon(start=3124777, stop=3125063)],
                assembly_id='GRCh38',
                coordinate_system=dat.CoordinateSystem.one_based(),
            ),
        ],
        rna_type='SRP_RNA',
        url='http://www.ensembl.org/Homo_sapiens/Transcript/Summary?t=ENST00000620330.1',
        seq_version='1',
        lineage=(
            "Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; "
            "Euteleostomi; Mammalia; Eutheria; Euarchontoglires; Primates; "
            "Haplorrhini; Catarrhini; Hominidae; Homo; Homo sapiens"
        ),
        chromosome="12",
        parent_accession='12.GRCh38',
        common_name='human',
        species='Homo sapiens',
        gene='RF00017',
        locus_tag='RF00017',
        optional_id='ENSG00000278469.1',
        description='Homo sapiens (human) SRP RNA Metazoan signal recognition particle RNA',
        note_data={
            'transcript_id': ['ENST00000620330.1']
        },
        xref_data={
            "UCSC": ["ENST00000620330.1"],
            "RFAM_trans_name": ["RF00017.190-201"],
            "RNAcentral": ["URS0000AA28EF"],
        },
        references=[dat.IdReference('pmid', '27337980')],
        mol_type='genomic DNA',
        pseudogene='N',
        is_composite='N',
    ))

    del ans['sequence']
    assert val == ans


def test_it_assigns_related(human_x):
    assert entry_for(human_x, "ENST00000434938.7").related_sequences == [dat.RelatedSequence(
        sequence_id="ENST00000430235.7",
        relationship='isoform'
    )]

    assert entry_for(human_x, "ENST00000430235.7").related_sequences == [dat.RelatedSequence(
        sequence_id="ENST00000434938.7",
        relationship='isoform'
    )]


def test_it_always_has_valid_rna_types_for_human(human_12):
    for entry in human_12:
        assert entry.rna_type in set([
            'SRP_RNA',
            'Y_RNA',
            'antisense_RNA',
            'lncRNA',
            'misc_RNA',
            'other',
            'precursor_RNA',
            'rRNA',
            'ribozyme',
            'snRNA',
            'snoRNA',
            'tRNA',
            'telomerase_RNA',
            'tmRNA',
        ])


def test_it_has_last_ncrna(human_12):
    assert entry_for(human_12, "ENST00000459107.1").xref_data == {
        'RNAcentral': ["URS00006F58F8"],
        'RFAM_trans_name': ['RF00019.633-201'],
        "UCSC": ["ENST00000459107.1"],
    }


def test_extracts_all_gencode_entries(human_12):
    assert len([e for e in human_12 if e.database == 'GENCODE']) == 1497


def test_can_build_gencode_entries(human_12):
    val = attr.asdict(entry_for(human_12, 'GENCODE:ENST00000620330.1'))
    del val['sequence']
    ans = attr.asdict(dat.Entry(
        primary_id='ENST00000620330',
        accession='GENCODE:ENST00000620330.1',
        ncbi_tax_id=9606,
        database='GENCODE',
        sequence='A',
        regions=[
            dat.SequenceRegion(
                chromosome='12',
                strand=1,
                exons=[dat.Exon(start=3124777, stop=3125063)],
                assembly_id='GRCh38',
                coordinate_system=dat.CoordinateSystem.one_based(),
            ),
        ],
        rna_type='SRP_RNA',
        url='',
        seq_version='1',
        lineage=(
            "Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; "
            "Euteleostomi; Mammalia; Eutheria; Euarchontoglires; Primates; "
            "Haplorrhini; Catarrhini; Hominidae; Homo; Homo sapiens"
        ),
        chromosome="12",
        parent_accession='12.GRCh38',
        common_name='human',
        species='Homo sapiens',
        gene='RF00017',
        locus_tag='RF00017',
        optional_id=None,
        description='Homo sapiens (human) SRP RNA Metazoan signal recognition particle RNA',
        note_data={
            'transcript_id': ['ENST00000620330.1']
        },
        xref_data={
            "UCSC": ["ENST00000620330.1"],
            "RFAM_trans_name": ["RF00017.190-201"],
            "RNAcentral": ["URS0000AA28EF"],
            'Ensembl': ['ENST00000620330.1'],
        },
        references=[dat.IdReference('pmid', '22955987')],
        mol_type='genomic DNA',
        pseudogene='N',
        is_composite='N',
    ))

    del ans['sequence']
    assert val == ans


def test_can_use_mouse_models_to_correct_rna_type(mouse_3):
    assert entry_for(mouse_3, 'ENSMUST00000082862.1').rna_type == 'telomerase_RNA'


def test_it_always_has_valid_rna_types_for_mouse(mouse_3):
    for entry in mouse_3:
        assert entry.rna_type in set([
            'SRP_RNA',
            'Y_RNA',
            'antisense_RNA',
            'lncRNA',
            'misc_RNA',
            'other',
            'precursor_RNA',
            'rRNA',
            'ribozyme',
            'snRNA',
            'snoRNA',
            'tRNA',
            'telomerase_RNA',
            'tmRNA',
        ])


def test_it_never_has_bad_vault(mouse_3):
    for entry in mouse_3:
        assert entry.rna_type != 'vaultRNA'


def test_does_not_append_none_to_description(macaca):
    assert entry_for(macaca, 'ENSMMUT00000062476.1').description == 'Macaca mulatta (rhesus monkey) lncRNA'


def test_does_not_create_extra_gencode_entries(macaca):
    assert len([e for e in macaca if e.database == 'GENCODE']) == 0
