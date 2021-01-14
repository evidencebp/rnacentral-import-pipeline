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

import re
import typing as ty

from rnacentral_pipeline.rnacentral.precompute.data.sequence import Sequence


def short_description(description: str, sequence: Sequence) -> str:
    """
    Shorten a description to remove the leading species (common name) from
    description. This is useful for display in the genome browser.
    """

    patterns: ty.Set[str] = set()
    for acc in sequence.accessions:
        patterns.update(re.escape(str(s)) for s in acc.all_species if s)
        patterns.update(re.escape(f"({c})") for c in acc.all_common_names if c)

    for pattern in patterns:
        description = re.sub("^" + pattern, "", description, flags=re.IGNORECASE)
        description = description.strip()

    description = re.sub(r"^\s*(\(\))?\s*", "", description)

    if (
        description.startswith("(")
        and description.endswith(")")
        and ")" not in description[1:-1]
    ):
        description = description[1:-1]

    return description
