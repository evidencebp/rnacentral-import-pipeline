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

from rnacentral_pipeline.rnacentral.precompute.description import \
    description_of

from .helpers import load_data



@pytest.mark.parametrize('rna_id,rna_type,name', [  # pylint: disable=no-member
    ('URS00001DEEBE_562', 'tRNA', 'Escherichia coli tRNA-Pro (CGG) (tRNA-Pro-CGG-1-1)'),
    ('URS0000661037_7955', 'tRNA', 'Danio rerio tRNA'),
    ('URS0000569A4A_9606', 'snoRNA', 'Homo sapiens small Cajal body-specific RNA 10 (SCARNA10)'),
    ('URS00003BECAC_9606', 'lncRNA', 'Homo sapiens long intergenic non-protein coding RNA 1729 (LINC01729)'),
    ('URS000075A546_9606', 'precursor_RNA', 'Homo sapiens (human) microRNA precursor (hsa-mir-3648-1, hsa-mir-3648-2)'),
    ('URS000075CC93_9606', 'precursor_RNA', 'Homo sapiens (human) microRNA precursor (hsa-mir-1302-2, hsa-mir-1302 9 to 11)'),
    ('URS000075C808_9606', 'lncRNA', 'Homo sapiens HOX transcript antisense RNA (HOTAIR)'),
    ('URS00000F9D45_9606', 'rRNA', 'Homo sapiens RNA, 5S ribosomal 1 (RNA5S1-8, RNA5S10-17)'),
    ('URS0000ABD87F_9606', 'rRNA', 'Homo sapiens RNA, 45S pre-ribosomal 4 (RNA45S4, RNA45SN1)'),
    ('URS000019E0CD_9606', 'lncRNA', 'Homo sapiens HELLP associated long non-coding RNA (HELLPAR)'),
    ('URS00006CE02F_9606', 'snoRNA', 'Homo sapiens (human) small nucleolar RNA SNORD118L8'),
    ('URS000018EB2E_3702', 'lncRNA', 'Arabidopsis thaliana (thale cress) Long non-coding antisense RNA COOLAIR'),
    ('URS00005F4CAF_3702', 'tRNA', 'Arabidopsis thaliana (thale cress) tRNA-Met(CAT)'),
    ('URS000048B30C_3702', 'tRNA', 'Arabidopsis thaliana (thale cress) partial tRNA-Leu'),

    # Failing because we have no data for it
    # ('URS00006A2469_3702', 'tRNA', 'Arabidopsis thaliana tRNA'),

    ('URS00003AC4AA_3702', 'siRNA', 'Arabidopsis thaliana (thale cress) TAS3/TASIR-ARF (TRANS-ACTING SIRNA3); other RNA (AT3G17185)'),
    ('URS00006550DA_10090', 'snoRNA', 'Mus musculus small Cajal body-specific RNA 1 (Scarna13), guide RNA'),
    ('URS000051DCEC_10090', 'snoRNA', 'Mus musculus small nucleolar RNA, C/D box 17 (Snord17), small nucleolar RNA'),
    ('URS000060B496_10090', 'snoRNA', 'Mus musculus small nucleolar RNA, H/ACA box 3 (Snora3), small nucleolar RNA'),
    ('URS00004E52D3_10090', 'lncRNA', 'Mus musculus predicted gene 12238 (Gm12238)'),
    ('URS00008E3A1B_10090', 'lncRNA', 'Mus musculus predicted gene 11532 (Gm11532)'),
    ('URS00006B3271_10090', 'snoRNA', 'Mus musculus small Cajal body-specific RNA 2 (Scarna2)'),
    ('URS0000A86584_10090', 'ncRNA', 'Mus musculus predicted gene 29254 (Gm29254)'),
    ('URS00007150F8_9913', 'precursor_RNA', 'Bos taurus (cattle) microRNA 431 precursor'),

    # Failing because bad PDBe RNA type
    # ('URS0000669B12_9913', 'tRNA', 'transfer RNA-Trp from Bos taurus (PDB 2AKE, chain B)'),

    ('URS00006D80BC_9913', 'precursor_RNA', 'Bos taurus (cattle) microRNA bta-mir-497 precursor'),
    ('URS000075CF25_9913', 'precursor_RNA', 'Bos taurus (cattle) microRNA bta-mir-10a precursor'),
    ('URS00003EBD9A_9913', 'telomerase_RNA', 'Bos taurus telomerase RNA component (TERC), telomerase RNA'),
    ('URS00005511ED_6239', 'lncRNA', 'Caenorhabditis elegans long non-coding RNA linc-125'),
    ('URS00004FB44B_6239', 'rRNA', 'Caenorhabditis elegans 26s rRNA'),
    ('URS0000466DE6_6239', 'miRNA', 'Caenorhabditis elegans microRNA cel-miR-229-5p'),
    ('URS00006DC8B9_6239', 'tRNA', 'Caenorhabditis elegans tRNA-Undet'),
    ('URS000069D7FA_6239', 'tRNA', 'Caenorhabditis elegans tRNA-His'),
    ('URS00002F21DA_7227', 'precursor_RNA', 'Drosophila melanogaster (fruit fly) microRNA dme-bantam precursor'),
    ('URS00004E9E38_7227', 'miRNA', 'Drosophila melanogaster (fruit fly) microRNA dme-bantam-3p'),
    ('URS000055786A_7227', 'miRNA', 'Drosophila melanogaster (fruit fly) microRNA dme-bantam-5p'),
    ('URS00000AEE53_380749', 'tmRNA', 'Hydrogenobaculum sp. Y04AAS1 tmRNA'),
    ('URS00009E8F92_885695', 'rRNA', 'Sinumelon nullarboricum partial 16S ribosomal RNA'),
    ('URS0000808D70_1478174', 'tmRNA', 'Neochlamydia sp. TUME1 tmRNA'),
    ('URS000037602E_9606', 'tmRNA', 'Homo sapiens (human) transfer-messenger RNA Esche_coli_K12'),
])
def test_computes_correct_species_specific_descriptions(rna_id, rna_type, name):
    data = load_data(rna_id)
    assert description_of(rna_type, data) == name


# @pytest.mark.parametrize('upi,rna_type,name', [
#     ('URS0000181AEC', 'tRNA', 'tRNA from 3413 species'),
# ])
# def test_computes_correct_generic_names(upi, rna_type, name):
#     data = fetch.entry(db(), upi)
#     assert description_of(rna_type, data) == name
