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

from tasks.config import db
from tasks.config import output
from tasks.config import rnacentral as rnac
from tasks.utils.compress import CompressTask

from rnacentral.utils import upi_ranges

from .xml_exporter import XmlExporterTask


class Search(luigi.WrapperTask):  # pylint: disable=R0904
    """
    This is a wrapper task for all search related tasks (that is it will do an
    xml export for all entries.
    """

    def requires(self):
        config = rnac()
        for start, stop in upi_ranges(config.xml_export_size, db()):
            xml_task = XmlExporterTask(min=start, max=stop)
            xml_file = xml_task.output().fn
            yield CompressTask(
               filename=xml_file,
               final_directory=output().search_files
            )
