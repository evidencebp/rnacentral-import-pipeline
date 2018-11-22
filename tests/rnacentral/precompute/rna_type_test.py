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

from rnacentral_pipeline.rnacentral.precompute.rna_type import rna_type_of

from .helpers import load_data


@pytest.mark.parametrize('rna_id,rna_type', [  # pylint: disable=no-member
    # pytest.param('URS0000A85A32_10090', 'tRNA', mark=pytest.mark.xfail),
    # pytest.param('URS000060C682_9606', 'vault_RNA', mark=pytest.mark.xfail("Inactive sequence"),
    # pytest.param('URS0000175007_7227', 'miRNA', mark=pytest.mark.xfail("Inactive sequence")),

    ('URS00000101E5_9606', 'lncRNA'),
    ('URS0000016972_6239', 'miRNA'),
    ('URS000001E7BA_559292', 'tRNA'),
    ('URS00000478B7_9606', 'SRP_RNA'),
    ('URS0000086133_9606', 'misc_RNA'),
    ('URS00000AEE53_380749', 'tmRNA'),
    ('URS00000B3045_7227', 'guide_RNA'),
    ('URS00000DA486_3702', 'other'),
    ('URS00000F9D45_9606', 'rRNA'),
    ('URS000012DE89_9606', 'autocatalytically_spliced_intron'),
    ('URS0000130A6B_3702', 'precursor_RNA'),
    ('URS000013F331_9606', 'RNase_P_RNA'),
    ('URS0000157BA2_4896', 'antisense_RNA'),
    ('URS000015995E_4615', 'miRNA'),
    ('URS000018EB2E_3702', 'lncRNA'),
    ('URS0000193C7E_9606', 'scRNA'),
    ('URS000019E0CD_9606', 'lncRNA'),
    ('URS00001DEEBE_562', 'tRNA'),
    ('URS00001E2C22_3702', 'rRNA'),
    ('URS000021515D_322710', 'autocatalytically_spliced_intron'),
    ('URS000024083D_9606', 'SRP_RNA'),
    ('URS000025C52E_9606', 'other'),
    ('URS00002963C4_4565', 'SRP_RNA'),
    ('URS00002AE808_10090', 'miRNA'),  # ENA has it as piRNA
    ('URS00002F216C_36329', 'antisense_RNA'),
    ('URS00002F21DA_7227', 'precursor_RNA'),
    ('URS00003054F4_6239', 'piRNA'),
    ('URS000032B6B6_9606', 'snRNA'),
    ('URS000034C5CB_7227', 'SRP_RNA'),
    ('URS000037602E_9606', 'tmRNA'),
    ('URS00003AC4AA_3702', 'other'),
    ('URS00003BECAC_9606', 'lncRNA'),
    ('URS00003CE153_9606', 'lncRNA'),
    ('URS00003EBD9A_9913', 'telomerase_RNA'),
    ('URS00003EE18C_9544', 'vault_RNA'),
    ('URS0000409697_3702', 'tRNA'),
    ('URS000040F7EF_4577', 'siRNA'),
    ('URS000045EBF2_9606', 'lncRNA'),
    ('URS0000466DE6_6239', 'miRNA'),
    ('URS000048B30C_3702', 'tRNA'),
    ('URS000049E122_9606', 'misc_RNA'),
    ('URS00004A2461_9606', 'Y_RNA'),
    ('URS00004B11CA_223283', 'scRNA'),
    ('URS00004E52D3_10090', 'lncRNA'),
    ('URS00004E9E38_7227', 'miRNA'),
    ('URS00004FB44B_6239', 'rRNA'),
    ('URS000051DCEC_10090', 'snoRNA'),
    ('URS00005511ED_6239', 'lncRNA'),
    ('URS000055786A_7227', 'miRNA'),
    ('URS0000563A36_7227', 'snoRNA'),
    ('URS0000564CC6_224308', 'tmRNA'),
    ('URS0000569A4A_9606', 'snoRNA'),
    ('URS000059A8B2_7227', 'rasiRNA'),
    ('URS000059EA49_32644', 'tmRNA'),
    ('URS00005A245E_10090', 'tRNA'),
    ('URS00005CDD41_352472', 'RNase_P_RNA'),
    ('URS00005CF03F_9606', 'Y_RNA'),
    ('URS00005D0BAB_9606', 'piRNA'),
    ('URS00005EF0FF_4577', 'siRNA'),
    ('URS00005F2C2D_4932', 'rRNA'),
    ('URS00005F4CAF_3702', 'tRNA'),
    ('URS000060B496_10090', 'snoRNA'),
    ('URS000061DECF_1235461', 'autocatalytically_spliced_intron'),
    ('URS000061F377_559292', 'rRNA'),
    ('URS00006233F9_9606', 'ribozyme'),
    ('URS000064A09E_13616', 'vault_RNA'),
    ('URS00006550DA_10090', 'snoRNA'),
    ('URS000065BB41_7955', 'other'),
    ('URS0000661037_7955', 'tRNA'),
    ('URS000069D7FA_6239', 'tRNA'),
    ('URS00006A938C_10090', 'ribozyme'),
    ('URS00006B14E9_6183', 'hammerhead_ribozyme'),
    ('URS00006B3271_10090', 'snoRNA'),
    ('URS00006BA413_9606', 'snoRNA'),
    ('URS00006C670E_30608', 'hammerhead_ribozyme'),
    ('URS00006CE02F_9606', 'snoRNA'),
    ('URS00006D80BC_9913', 'precursor_RNA'),
    ('URS00006DC8B9_6239', 'tRNA'),
    ('URS0000714027_9031', 'other'),
    ('URS00007150F8_9913', 'precursor_RNA'),
    ('URS000072A167_10141', 'Y_RNA'),
    ('URS0000732D5D_9606', 'lncRNA'),
    ('URS0000734D8F_9606', 'snRNA'),
    ('URS0000759BEC_9606', 'lncRNA'),
    ('URS000075A336_9606', 'miRNA'),
    ('URS000075A546_9606', 'precursor_RNA'),
    ('URS000075C290_9606', 'precursor_RNA'),
    ('URS000075C808_9606', 'lncRNA'),
    ('URS000075CC93_9606', 'precursor_RNA'),
    ('URS000075CF25_9913', 'precursor_RNA'),
    ('URS000075EF5D_9606', 'snRNA'),
    ('URS0000764CCC_1415657', 'RNase_P_RNA'),
    ('URS000077FBEB_9606', 'lncRNA'),
    ('URS00007A9FDC_6239', 'misc_RNA'),
    ('URS00007FD8A3_7227', 'lncRNA'),
    ('URS0000808D19_644', 'hammerhead_ribozyme'),
    ('URS0000808D70_1478174', 'tmRNA'),
    ('URS000080DD33_32630', 'ribozyme'),
    ('URS000080DFDA_32630', 'hammerhead_ribozyme'),
    ('URS000082AF7D_5699', 'guide_RNA'),
    ('URS000083F182_242161', 'other'),
    ('URS000086852D_32630', 'hammerhead_ribozyme'),
    ('URS00008E398A_9606', 'snoRNA'),
    ('URS00008E3A1B_10090', 'lncRNA'),
    ('URS000092FF0A_9371', 'snoRNA'),
    ('URS00009E8F92_885695', 'rRNA'),
    ('URS0000A17B82_640938', 'other'),
    ('URS0000A767C0_3702', 'lncRNA'),
    ('URS0000A86584_10090', 'lncRNA'),
    ('URS0000A8F612_9371', 'snoRNA'),
    ('URS0000A994FE_9606', 'other'),
    ('URS0000ABD7EF_9606', 'rRNA'),
    ('URS0000ABD87F_9606', 'rRNA'),
])
def test_computes_correct_rna_types(rna_id, rna_type):
    data = load_data(rna_id)
    assert rna_type_of(data) == rna_type
