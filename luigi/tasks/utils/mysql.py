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

from rnacentral.mysql import MysqlWrapper

from tasks.utils.files import atomic_output


class MysqlQueryTask(luigi.Task):
    db_url = luigi.Parameter()
    query = luigi.Parameter()
    local_path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.local_path)

    def run(self):
        mysql = MysqlWrapper.from_url(self.db_url)
        with atomic_output(self.output()) as out:
            mysql.write_query(out, self.query)