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
    ('URS0000000DBF_6239', 'piRNA'),
    ('URS0000005270_9606', 'rRNA_5_8S'),
    ('URS00000081EA_9606', 'U1_snRNA'),
    ('URS00000101E5_9606', 'lnc_RNA'),
    ('URS0000016972_6239', 'miRNA'),
    ('URS000001E7BA_559292', 'tRNA'),
    ('URS00000478B7_9606', 'SRP_RNA'),
    ('URS00000490A3_6239', 'miRNA'),
    ('URS000004F67F_109352', 'rRNA_primary_transcript'),
    ('URS0000050E80_67003', 'rRNA_primary_transcript'),
    ('URS000006F31F_4932', 'RNase_MRP_RNA'),
    ('URS00000AEE53_380749', 'tmRNA'),
    ('URS00000B3045_7227', 'H_ACA_box_snoRNA'),
    ('URS00000CF490_2786', 'small_subunit_rRNA'),
    ('URS00000DA486_3702', 'siRNA'),
    ('URS00000F9D45_9606', 'rRNA_5S'),
    ('URS00000FFD14_109352', 'rRNA_primary_transcript'),
    ('URS0000118C49_9606', 'U5_snRNA'),
    ('URS00001232FE_175275', 'small_subunit_rRNA'),
    ('URS000012DE89_9606', 'autocatalytically_spliced_intron'),
    ('URS0000130A6B_3702', 'pre_miRNA'),
    ('URS00001380AF_9606', 'U5_snRNA'),
    ('URS000013F331_9606', 'RNase_P_RNA'),
    ('URS0000149178_9606', 'U4_snRNA'),
    ('URS000015995E_4615', 'miRNA'),
    ('URS000015F227_9606', 'scaRNA'),
    ('URS0000162C88_9606', 'rRNA_5_8S'),
    ('URS00001872A7_9606', 'U6_snRNA'),
    ('URS000018EB2E_3702', 'lnc_RNA'),
    ('URS0000193C7E_9606', 'lnc_RNA'),
    ('URS000019E0CD_9606', 'lnc_RNA'),
    ('URS00001B2620_9606', 'scaRNA'),
    ('URS00001D1383_1299', 'Y_RNA'),
    ('URS00001DEEBE_562', 'tRNA'),
    ('URS00001E2C22_3702', 'rRNA_5_8S'),
    ('URS00001F11B5_6239', 'spliced_leader_RNA'),
    ('URS00002078D9_216597', 'Y_RNA'),
    ('URS000020CEFD_9606', 'pre_miRNA'),
    ('URS0000210B3E_216597', 'Y_RNA'),
    ('URS000021515D_322710', 'group_II_intron'),
    ('URS000021BC29_9606', 'scaRNA'),
    ('URS000024083D_9606', 'SRP_RNA'),
    ('URS000024F0F7_4932', 'H_ACA_box_snoRNA'),
    ('URS00002963C4_4565', 'SRP_RNA'),
    ('URS00002985F4_3094', 'rRNA_large_subunit_primary_transcript'),
    ('URS00002AE808_10090', 'miRNA'),
    ('URS00002B64E6_7227', 'scaRNA'),  # Why flybase disagree?
    ('URS00002BF60E_7227', 'scaRNA'),  # Why flybase disagree?
    ('URS00002F216C_36329', 'antisense_RNA'),
    ('URS00002F21DA_7227', 'pre_miRNA'),
    ('URS00003054F4_6239', 'piRNA'),
    ('URS000032B6B6_9606', 'U1_snRNA'),
    ('URS000034C5CB_7227', 'SRP_RNA'),
    ('URS000036E62B_9593', 'pre_miRNA'),
    ('URS000037602E_9606', 'tmRNA'),
    ('URS00003AC4AA_3702', 'siRNA'),
    ('URS00003BECAC_9606', 'lnc_RNA'),
    ('URS00003CE153_9606', 'lnc_RNA'),
    ('URS00003EBD9A_9913', 'telomerase_RNA'),
    ('URS00003EE18C_9544', 'vault_RNA'),
    ('URS00003EE995_9606', 'U2_snRNA'),
    ('URS00003F07BD_9606', 'U4_snRNA'),
    ('URS0000409697_3702', 'tRNA'),
    ('URS000040F7EF_4577', 'siRNA'),
    ('URS00004151E2_5693', 'SRP_RNA'),
    ('URS0000443498_9606', 'U6atac_snRNA'),
    ('URS000045EBF2_9606', 'lnc_RNA'),
    ('URS0000466DE6_6239', 'miRNA'),
    ('URS000048B30C_3702', 'tRNA'),
    ('URS000049E122_9606', 'ncRNA'),
    ('URS000049EC81_7227', 'scaRNA'),
    ('URS00004A2461_9606', 'Y_RNA'),
    ('URS00004E52D3_10090', 'snoRNA'),
    ('URS00004E9E38_7227', 'miRNA'),
    ('URS00004FB44B_6239', 'rRNA_25S'),
    ('URS0000508014_7227', 'scaRNA'),  # Why flybase disagree?
    ('URS000051DCEC_10090', 'C_D_box_snoRNA'),
    ('URS000053F313_559292', 'U5_snRNA'),
    ('URS00005511ED_6239', 'snoRNA'),
    ('URS000055786A_7227', 'miRNA'),
    ('URS0000563A36_7227', 'snoRNA'),
    ('URS0000564CC6_224308', 'tmRNA'),
    ('URS0000569A4A_9606', 'scaRNA'),
    ('URS000059A8B2_7227', 'rasiRNA'),
    ('URS000059EA49_32644', 'tmRNA'),
    ('URS00005A245E_10090', 'tRNA'),
    ('URS00005A2612_9606', 'H_ACA_box_snoRNA'),
    ('URS00005CDD41_352472', 'RNase_P_RNA'),
    ('URS00005CF03F_9606', 'Y_RNA'),
    ('URS00005D0BAB_9606', 'piRNA'),
    ('URS00005EB5B7_78454', 'pre_miRNA'),
    ('URS00005EB5B7_9447', 'pre_miRNA'),
    ('URS00005EB5B7_9509', 'pre_miRNA'),
    ('URS00005EB5B7_9519', 'pre_miRNA'),
    ('URS00005EB5B7_9593', 'pre_miRNA'),
    ('URS00005EF0FF_4577', 'siRNA'),
    ('URS00005F2C2D_4932', 'rRNA_18S'),
    ('URS00005F4CAF_3702', 'tRNA'),
    ('URS00005FCB94_9606', 'U4_snRNA'),
    ('URS000060B496_10090', 'H_ACA_box_snoRNA'),
    ('URS000061DECF_1235461', 'group_II_intron'),
    ('URS000061F377_559292', 'rRNA_25S'),
    ('URS00006233F9_9606', 'ribozyme'),
    ('URS000063164F_9606', 'U2_snRNA'),
    ('URS0000631BD4_9606', 'U5_snRNA'),
    ('URS000064A09E_13616', 'vault_RNA'),
    ('URS00006550DA_10090', 'scaRNA'),
    ('URS000065BB41_7955', 'scRNA'),
    ('URS0000661037_7955', 'tRNA'),
    ('URS0000675C1B_9796', 'U6atac_snRNA'),
    ('URS000069D7FA_6239', 'tRNA'),
    ('URS00006B14E9_6183', 'hammerhead_ribozyme'),
    ('URS00006B3271_10090', 'scaRNA'),
    ('URS00006BA413_9606', 'C_D_box_snoRNA'),
    ('URS00006C1AB2_9606', 'U6atac_snRNA'),
    ('URS00006C670E_30608', 'hammerhead_ribozyme'),
    ('URS00006CE02F_9606', 'C_D_box_snoRNA'),
    ('URS00006D80BC_9913', 'pre_miRNA'),
    ('URS00006DC8B9_6239', 'tRNA'),
    ('URS00006F5B4D_9606', 'U4atac_snRNA'),
    ('URS000070D8C8_9606', 'U6atac_snRNA'),
    ('URS0000714027_9031', 'scRNA'),
    ('URS00007150F8_9913', 'pre_miRNA'),
    ('URS0000715A86_9606', 'U4_snRNA'),
    ('URS000072A167_10141', 'Y_RNA'),
    ('URS0000732D5D_9606', 'lnc_RNA'),
    ('URS0000734D8F_9606', 'snRNA'),
    ('URS0000759BEC_9606', 'lnc_RNA'),
    ('URS000075A336_9606', 'miRNA'),
    ('URS000075A546_9606', 'pre_miRNA'),
    ('URS000075AD80_9606', 'U1_snRNA'),
    ('URS000075ADBA_9606', 'U4atac_snRNA'),
    ('URS000075BAAE_9606', 'U5_snRNA'),
    ('URS000075C290_9606', 'pre_miRNA'),
    ('URS000075C808_9606', 'lnc_RNA'),
    ('URS000075CC93_9606', 'pre_miRNA'),
    ('URS000075CD30_9606', 'U1_snRNA'),
    ('URS000075CF25_9913', 'pre_miRNA'),
    ('URS000075D341_9606', 'rRNA_5_8S'),
    ('URS000075EF5D_9606', 'U12_snRNA'),
    ('URS0000764CCC_1415657', 'RNase_P_RNA'),
    ('URS000077FBEB_9606', 'lnc_RNA'),
    ('URS00007CD270_1872691', 'rRNA_18S'),
    ('URS00007FD8A3_7227', 'lnc_RNA'),
    ('URS0000808D19_644', 'hammerhead_ribozyme'),
    ('URS0000808D70_1478174', 'tmRNA'),
    ('URS000080DD33_32630', 'group_I_intron'),
    ('URS000080DE76_9606', 'rRNA_5_8S'),
    ('URS000082AF7D_5699', 'guide_RNA'),
    ('URS000083F182_242161', 'tRNA'),
    ('URS000086852D_32630', 'hammerhead_ribozyme'),
    ('URS00008E398A_9606', 'H_ACA_box_snoRNA'),
    ('URS00008E39F3_7227', 'scaRNA'),  # Why flybase disagree?
    ('URS00008E3A1B_10090', 'lnc_RNA'),
    ('URS000091C11A_9606', 'rRNA_28S'),
    ('URS000092FF0A_9371', 'snoRNA'),
    ('URS00009E8F92_885695', 'rRNA_16S'),
    ('URS0000A17B82_640938', 'sequence_feature'),
    ('URS0000A767C0_3702', 'lnc_RNA'),
    ('URS0000A770BD_3702', 'U6atac_snRNA'),
    ('URS0000A7BB1C_9606', 'U4_snRNA'),
    ('URS0000A85A32_10090', 'tRNA'),
    ('URS0000A86584_10090', 'lnc_RNA'),
    ('URS0000A8F612_9371', 'scaRNA'),
    ('URS0000A96391_9606', 'U4_snRNA'),
    ('URS0000A994FE_9606', 'ncRNA'),
    ('URS0000ABD7E8_9606', 'rRNA_primary_transcript'),
    ('URS0000ABD7EF_9606', 'rRNA_28S'),
    ('URS0000ABD87F_9606', 'rRNA_primary_transcript'),
    ('URS0000ABD8C6_9606', 'rRNA_primary_transcript'),
    ('URS0000D56C46_9606', 'pre_miRNA'),
    ('URS0000EF7A6A_6945', 'U12_snRNA'),
    ('URS000075CEC3_9606', 'miRNA'),
    ('URS0000EEE7A7_9606', 'SRP_RNA'),

    # # Not sure SO term
    # ('URS000018B855_1270', 'misc_RNA'),
    # ('URS0000127C85_175245', 'misc_RNA'),
    # ('URS000080DFDA_32630', 'hammerhead_ribozyme'),  # Is there a term for fragments?
    # ('URS00007A9FDC_6239', 'misc_RNA'),  # Some sort of other?
    # ('URS000025C52E_9606', 'other'),
    # ('URS0000086133_9606', 'misc_RNA'),
    # ('URS00006A938C_10090', 'ribozyme'),
    # ('URS00004B11CA_223283', 'scRNA'),  # Is there an sRNA term?
    # ('URS0000157BA2_4896', 'antisense_RNA'),
    # ('URS0000ABD7E9_9606', 'snoRNA_gene'),

    # Known failing
    pytest.param('URS000060C682_9606', 'vault_RNA', marks=pytest.mark.xfail(reason="Inactive sequence")),
    pytest.param('URS0000175007_7227', 'miRNA', marks=pytest.mark.xfail(reason="Inactive sequence")),

])
def test_computes_correct_rna_types(rna_id, rna_type):
    data = load_data(rna_id)
    assert rna_type_of(data) == rna_type
