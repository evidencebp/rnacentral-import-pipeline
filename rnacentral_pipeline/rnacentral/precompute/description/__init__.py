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

from . import generic
from . import species_specific as species


def description_of(rna_type, sequence):
    """
    The entry point for using the rule based approach for descriptions. This
    approach works in two stages, first it determines the rna_type of the
    sequence and then it will select the description from all xrefs of the
    sequence which match the given rna_type.

    If a taxid is given then a species specific name is generated, otherwise a
    more general cross species name is created.

    Parameters
    ----------
    sequence : Rna
        The sequence to create a description for.

    xrefs : iterable
        A list of xrefs to use for determining the rna_type as well as the
        description.

    taxid : int, None
        The taxon id for the sequence.

    Returns
    -------
    description : str, None
        The description of the sequence
    """

    if not rna_type:
        raise ValueError("Must have definied RNA type to get a description")

    if sequence.is_species_specific():
        return species.description_of(rna_type, sequence)
    return generic.description_of(rna_type, sequence)
