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
import luigi

from tasks.utils.pgloader import PGLoader
from tasks.config import genome_mapping
from .genome_mapping_tasks import ParseBlatOutput
from .pgload_exact_matches import GenomeMappingPGLoadExactMatches


CONTROL_FILE = """LOAD CSV
FROM '{filename}'
HAVING FIELDS
(
    rna_id,
    upi,
    taxid,
    unused_field,
    region_id,
    chromosome,
    start,
    stop,
    strand,
    assembly_id,
    identity
)
INTO {db_url}
TARGET COLUMNS
(
    rna_id,
    upi,
    taxid,
    region_id,
    chromosome,
    start,
    stop,
    strand,
    assembly_id,
    identity
)
WITH
    fields terminated by '\t'
SET
    search_path = 'rnacen'
BEFORE LOAD DO
$$ DROP TABLE IF EXISTS {table}; $$,
$$ CREATE TABLE IF NOT EXISTS rnacen.{table} (
    rna_id varchar(50) NULL,
    upi varchar(13) NULL,
    taxid int4 NULL,
    region_id varchar(100) NULL,
    chromosome varchar(100) NULL,
    "start" int4 NULL,
    stop int4 NULL,
    strand varchar(10) NULL,
    assembly_id varchar(50) NULL,
    identity float8
); $$
AFTER LOAD DO
$$ DELETE FROM rnc_genome_mapping
WHERE identity < 1
AND assembly_id = '{assembly_id}';
$$,
$$ insert into rnc_genome_mapping (rna_id, upi, taxid, region_id, chromosome, "start", stop, strand, assembly_id, "identity") (
    select t1.rna_id, t1.upi, t1.taxid, t1.region_id, t1.chromosome, t1."start", t1.stop, t1.strand, t1.assembly_id, t1."identity"
    from load_genome_mapping t1
    left join rnc_genome_mapping t2
    on t1.rna_id = t2.rna_id
    where t2.rna_id is null
);
; $$,
$$ TRUNCATE TABLE {table}; $$,
$$
UPDATE rnc_rna_precomputed t1
SET has_coordinates = True
FROM rnc_genome_mapping t2
WHERE t2.assembly_id = '{assembly_id}'
AND t1.upi = t2.upi
AND t1.taxid = t2.taxid
; $$
;
"""


class GenomeMappingPGLoadInexactMatches(PGLoader):  # pylint: disable=R0904
    """
    """
    assembly_id = luigi.Parameter()
    species = luigi.Parameter()
    taxid = luigi.IntParameter()
    division = luigi.Parameter()

    def control_filename(self):
        return os.path.join(genome_mapping().species(self.species),
                            'pgloader-inexact-matches.ctl')

    def requires(self):
        return [
            ParseBlatOutput(taxid=self.taxid,
                           species=self.species,
                           assembly_id=self.assembly_id,
                           division=self.division),
            GenomeMappingPGLoadExactMatches(taxid=self.taxid,
                           species=self.species,
                           assembly_id=self.assembly_id,
                           division=self.division),
        ]

    def control_file(self):
        filename = self.input()[0]['inexact'].path
        table = 'load_genome_mapping'
        return CONTROL_FILE.format(
            filename=filename,
            db_url=self.db_url(table=table),
            table=table,
            assembly_id=self.assembly_id,
            search_path=self.db_search_path()
        )