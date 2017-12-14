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

from time import sleep
import collections as coll

import requests

from functools32 import lru_cache

from ..data import Reference

URL = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{pmid}&format=json'


class UnknownPmid(Exception):
    pass


class FailedPublicationId(Exception):
    pass


class TooManyPublications(Exception):
    pass


@lru_cache()
def summary(pmid):
    for count in xrange(5):
        response = requests.get(URL.format(pmid=pmid))
        try:
            response.raise_for_status()
            break
        except requests.HTTPError:
            if response.status_code == 500:
                sleep(0.1 * (count + 1))
                continue
        else:
            raise FailedPublicationId(pmid)

    data = response.json()
    assert data, "Somehow got no data"
    if data['hitCount'] == 0:
        raise UnknownPmid(pmid)

    if data['hitCount'] == 1:
        return data['resultList']['result'][0]

    raise TooManyPublications(pmid)


def reference(accession, pmid):
    data = summary(pmid)
    location = '{title} {volume} ({issue}):{pages} ({year})'.format(
        title=data['journalTitle'],
        issue=data['issue'],
        volume=data['journalVolume'],
        pages=data['pageInfo'],
        year=data['pubYear'],
    )

    return Reference(
        accession=accession,
        authors=data['authorString'],
        location=location,
        title=data['title'],
        pmid=int(pmid),
        doi=data.get('doi', None),
    )
