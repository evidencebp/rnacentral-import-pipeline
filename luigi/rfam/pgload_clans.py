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

from rfam.clans_csv import ClanCSV
from rfam.config import db as DBConfig

CONTROL_FILE = """
LOAD CSV
FROM '{filename}'
HAVING FIELDS
(
    rfam_clan_id,
    name,
    description,
    family_count
)
INTO postgresql://{user}:{password}@{host}:{port}/{db}?rnc_rfam_clans
TARGET COLUMNS
(
    rfam_clan_id,
    name,
    description,
    family_count
)
WITH 
    skip header = 1,
    fields escaped by double-quote,
    fields terminated by ','
;
"""


class PGLoadClans(PGLoader):
    def requires(self):
        return [
            ClanCSV(),
        ]

    def output(self):
        for requirement in self.requires():
            yield requirement.output()

    def filename(self):
        return self.requires()[0].output().fn

    def control_file(self):
        config = DBConfig()
        return CONTROL_FILE.format(
            filename=self.filename,
            user=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
            db=config.db_name,
        )


if __name__ == '__main__':
    luigi.run(main_task_cls=PGLoadClans)
