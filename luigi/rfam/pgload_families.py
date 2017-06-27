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

import luigi

from pgloader import PGLoader

from rfam.families_csv import FamiliesCSV
from rfam.pgload_clans import PGLoadClans
from rfam.config import db as DBConfig

CONTROL_FILE = """LOAD CSV
FROM '{filename}'
HAVING FIELDS
(
    rfam_model_id,
    name,
    description [null if blanks],
    rfam_clan_id [null if blanks],
    seed_count,
    full_count,
    length,
    domain [null if blanks],
    is_suppressed
)
INTO postgresql://{user}:{password}@{host}:{port}/{db}?load_rnc_rfam_models
TARGET COLUMNS
(
    rfam_model_id,
    name,
    description,
    rfam_clan_id,
    seed_count,
    full_count,
    length,
    domain,
    is_suppressed
)
WITH
    skip header = 1,
    fields escaped by double-quote,
    fields terminated by ','
;
BEFORE LOAD DO
$$
truncate table load_rnc_rfam_models;
$$
AFTER LOAD DO
$$ insert into rnc_rfam_models (
    rfam_model_id,
    name,
    description,
    seed_count,
    full_count,
    length,
    is_suppressed,
    rfam_clan_id,
    domain
) (
select
    rfam_model_id,
    name,
    description,
    seed_count,
    full_count,
    length,
    is_suppressed,
    rfam_clan_id,
    domain
from load_rnc_rfam_models
)
ON CONFLICT DO UPDATE;
$$,
$$
truncate table load_rnc_rfam_models;
$$
;
"""


class PGLoadFamilies(PGLoader):
    def requires(self):
        return [
            FamiliesCSV(),
            PGLoadClans(),
        ]

    def control_file(self):
        config = DBConfig()
        filename = FamiliesCSV().output().fn
        return CONTROL_FILE.format(
            filename=filename,
            user=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
            db=config.db_name,
        )


if __name__ == '__main__':
    luigi.run(main_task_cls=PGLoadFamilies)
