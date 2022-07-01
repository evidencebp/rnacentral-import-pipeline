# -*- coding: utf-8 -*-

"""
Copyright [2009-2020] EMBL-European Bioinformatics Institute
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

from rnacentral_pipeline.databases.data import Entry, Exon, SequenceRegion
from rnacentral_pipeline.databases.helpers import phylogeny as phy

import gffutils
from Bio import SeqIO

import pathlib
import typing as ty
import os

import pandas as pd


def _find_gff_file(search_path: pathlib.Path) -> pathlib.Path:
    """
    Find the right gff3 file for use with the fasta in parsing alongside the
    info file
    """
    for file in search_path.iterdir():
        if file.suffix == ".gff3" and "PLncDB" in file.stem:
            return file

def _find_fasta_file(search_path: pathlib.Path) -> pathlib.Path:
    """
    Find the fasta file that corresponds with the gff file and info file
    """
    for file in search_path.iterdir():
        if file.suffix == ".fa" and "PLncDB" in file.stem:
            return file

def _find_info_file(search_path: pathlib.Path) -> pathlib.Path:
    """
    Find the corresponding info filefor this fasta and gff
    """
    for file in search_path.iterdir():
        if file.suffix == ".txt" and "lncRNA" in file.stem:
            return file



def parse(data:pathlib.Path) -> ty.Iterable[Entry]:
    """
    Parse a directory of data from PLncDB into entries for import. Expects the
    directory to contain one directory per species which is derived from the
    FTP download that has been decompressed.

    We read the gff3, fasta, and associated info file to construct the entry
    """

    ## Set some things which will be common for all entries
    rna_type = "SO:0001877"
    database = "PLNCDB"

    url = "https://www.tobaccodb.org/plncdb/nunMir?plncdb_id={}"

    entries = []
    ## loop on all directories in the data directory
    for species_dir in data.iterdir():
        if not species_dir.is_dir():
            continue ## Skip any remaining normal files

        gff_file = _find_gff_file(species_dir)
        fasta_file = _find_fasta_file(species_dir)
        info_file = _find_info_file(species_dir)

        # Load the GFF file into the gffutils database for working with
        gff_db = gffutils.create_db(str(gff_file), ":memory:")

        ## Load the FASTA file as well
        fasta_db = SeqIO.to_dict(SeqIO.parse(fasta_file, 'fasta'))

        ## Finally, load the info file using pandas
        species_info = pd.read_csv(info_file, delimiter='\t')
        species_info["Species"] = species_info["Species"].apply(phy.taxid)



        for gene_id_q in gff_db.execute("select id from features"):
            primary_id = gene_id_q["id"]

            gene_info = species_info[species_info["lncRNA_ID"] == primary_id]
            if len(gene_info) == 0:
                break

            taxid = gene_info["Species"].values[0]

            sequence = fasta_db[primary_id]

            features = list(gff_db.children(primary_id))
            ##TODO: check coordinate system
            exons = [Exon(start=e.start, stop=e.stop) for e in features]


            region = SequenceRegion(
                chromosome = features[0].chrom,
                strand = features[0].strand,
                exons = exons,
                assembly_id = gene_info['Ref_Genome_Vers'],
                coordinate_system = "1-start, fully-closed"
            )


            entries.append(
                Entry(
                    primary_id=primary_id,
                    accession=primary_id,
                    ncbi_tax_id=int(taxid),
                    database=database,
                    sequence=sequence.seq,
                    regions=[region],
                    rna_type=rna_type,
                    url=url.format(primary_id),
                    seq_version="1",
                    # optional_id=optional_id(record, context),
                    description=" ",
                    # note_data=note_data(record),
                    # xref_data=xrefs(record),
                    # related_sequences=related_sequences(record),
                    # secondary_structure=secondary_structure(record),
                    # references=references(record),
                    # organelle=record.get("localization", None),
                    # product=record.get("product", None),
                    # anticodon=anticodon(record),
                    gene=gene_info["Gene_ID"].values[0],
                    # gene_synonyms=gene_synonyms(record),
                    # locus_tag=locus_tag(record),
                    # features=features(record),
                )
            )



    return entries
