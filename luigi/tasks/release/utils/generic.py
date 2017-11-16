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


def file_pattern(name):
    """
    Given a database name this will produce a pattern for pgloader to match
    files from that database. If the name is 'all' then a pattern that matches
    all files will be created. The file pattern is quoted using '#'.
    """
    pattern = name
    if name == 'all':
        pattern = 'chunk_*'
    else:
        pattern = '{pattern}*.csv'.format(pattern=pattern)
    return pattern