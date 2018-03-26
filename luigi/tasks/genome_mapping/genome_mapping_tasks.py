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

import os
import subprocess

import luigi

from glob import iglob

from tasks.config import db
from tasks.config import genome_mapping

from tasks.export.ftp.fasta.utils import FastaExportBase

from rnacentral.genome_mapping import genome_mapping as gm


class GetFasta(FastaExportBase):
    taxid = luigi.IntParameter(default=9606)

    def output(self):
        return luigi.LocalTarget(genome_mapping().rnacentral_fasta('%i.fa' % self.taxid))

    def records(self):
        return gm.export_rnacentral_fasta2(db(), taxid=self.taxid)


class CleanSplitFasta(luigi.Task):
    taxid = luigi.IntParameter(default=9606)
    chunks = luigi.IntParameter(default=100)
    min_length = luigi.IntParameter(default=20)
    max_length = luigi.IntParameter(default=100000)

    def requires(self):
        return GetFasta(taxid=self.taxid)

    def output(self):
        for i in xrange(1, self.chunks):
            chunk_fasta = os.path.join(genome_mapping().chunks(self.taxid),
                                       '{taxid}-clean.part_{id}.fasta'.format(
                                        taxid=self.taxid, id='%03d' % i))
            yield luigi.LocalTarget(chunk_fasta)

    def run(self):
        fasta = self.input().path
        out_dir = genome_mapping().chunks(self.taxid)
        gm.clean_split(min_length=self.min_length, max_length=self.max_length, fasta=fasta, chunks=self.chunks, out_dir=out_dir, taxid=self.taxid)


class GetChromosome(luigi.Task):
    taxid = luigi.IntParameter(default=9606)

    def output(self):
        genomes = {
            9606: 'GCA_000001405.25',
            10090: 'GCA_000001635.7',
            10116: 'GCA_000001895.4',
        }
        chromosomes = genome_mapping().genomes(genomes[self.taxid])
        for filename in iglob(os.path.join(chromosomes, '*.fa')):
            yield luigi.LocalTarget(filename)


class BlatJob(luigi.Task):
    """
    Run blat to map a fasta file with RNAcentral sequences to a chromosome.
    """
    taxid = luigi.IntParameter(default=9606)
    fasta_input = luigi.Parameter()
    chromosome = luigi.Parameter()

    def run(self):
        """
        """
        genome_path, _ = os.path.split(self.chromosome)
        cmd = ('blat -ooc={genome_path}/11.ooc -noHead -q=rna -stepSize=5 '
               '-repMatch=2253 -minScore=0 -minIdentity=95 '
               '{chromosome} {fasta_input} {psl_output} ').format(
               genome_path=genome_path,
               chromosome=self.chromosome,
               fasta_input=self.fasta_input,
               psl_output=self.output().path)
        status = subprocess.call(cmd, shell=True)
        if status != 0:
            raise ValueError('Failed to run blat: %s' % cmd)

    def output(self):
        """
        """
        _, fasta_name = os.path.split(self.fasta_input)
        _, chromosome_name = os.path.split(self.chromosome)
        psl_output = genome_mapping().blat_output(str(self.taxid))
        return luigi.LocalTarget(os.path.join(psl_output, '%s-%s.psl' % (chromosome_name, fasta_name)))


class ParsePslOutput(luigi.Task):
    """
    Run a shell script to transform psl output produced by blat into tsv files
    that can be loaded into the database.
    """
    taxid = luigi.IntParameter(default=4932)

    def get_blat_output(self):
        return genome_mapping().blat_output(str(self.taxid))

    def output(self):
        return [luigi.LocalTarget(os.path.join(self.get_blat_output(), 'mapping.tsv')),
        luigi.LocalTarget(os.path.join(self.get_blat_output(), 'mapping-inexact.tsv'))]

    def run(self):
        cmd = 'source scripts/psl2tsv.sh {blat_output}'.format(blat_output=self.get_blat_output())
        status = subprocess.call(cmd, shell=True)
        if status != 0:
            raise ValueError('Failed to run psl2tsv: %s' % cmd)
