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

import json
import logging
import operator as op
import itertools as it
from collections import Counter

import six

import attr
from attr.validators import and_
from attr.validators import instance_of as is_a

from rnacentral_pipeline.databases.helpers.hashes import md5
from rnacentral_pipeline.databases.helpers.hashes import crc64

from . import utils
from .references import Reference
from .references import IdReference
from .secondary_structure import SecondaryStructure

LOGGER = logging.getLogger(__name__)

FEATURE_TYPE_RNAS = set([
    'rRNA',
    'tRNA',
    'precursor_RNA',
    'tmRNA',
    'misc_RNA',
])


@attr.s(frozen=True)
class Entry(object):
    """
    This represents an RNAcentral entry that will be imported into the
    database. It should contain all the information needed to define all the
    data that is loaded from expert databases. For example it should contain
    information for rna (sequence), rnc_accessions, rnc_coordinates, and so
    forth.
    """

    # Also known as external_id
    primary_id = attr.ib(validator=is_a(six.text_type), convert=six.text_type)
    accession = attr.ib(validator=is_a(six.text_type), convert=six.text_type)
    ncbi_tax_id = attr.ib(validator=is_a(six.integer_types))
    database = attr.ib(
        validator=is_a(six.text_type),
        converter=lambda s: six.text_type(s.upper()),
    )
    sequence = attr.ib(validator=is_a(six.text_type), convert=six.text_type)
    # exons = attr.ib(validator=is_a(list))
    regions = attr.ib(validator=is_a(list))
    rna_type = attr.ib(
        validator=is_a(six.text_type),
        # validator=matches_pattern(SO_PATTERN),
        converter=utils.from_so_term,
    )
    url = attr.ib(validator=is_a(six.text_type), convert=six.text_type)
    seq_version = attr.ib(
        validator=and_(is_a(six.text_type), utils.matches_pattern(r'^\d+$')),
        converter=six.text_type,
    )

    note_data = utils.possibly_empty(dict)
    xref_data = utils.possibly_empty(dict)

    related_sequences = utils.possibly_empty(list)

    chromosome = utils.optionally(six.string_types)
    species = utils.optionally(six.string_types)
    common_name = utils.optionally(six.string_types)
    lineage = utils.optionally(six.string_types)
    gene = utils.optionally(six.string_types)
    locus_tag = utils.optionally(six.string_types)
    optional_id = utils.optionally(six.string_types)
    product = utils.optionally(six.string_types)
    parent_accession = utils.optionally(six.string_types)
    ordinal = utils.optionally(six.string_types)
    non_coding_id = utils.optionally(six.string_types)
    project = utils.optionally(six.string_types)
    keywords = utils.optionally(six.string_types)
    division = utils.optionally(six.string_types)
    organelle = utils.optionally(six.string_types)
    allele = utils.optionally(six.string_types)
    anticodon = utils.optionally(six.string_types)
    experiment = utils.optionally(six.string_types)
    function = utils.optionally(six.string_types)
    inference = utils.optionally(six.string_types)
    map = utils.optionally(six.string_types)
    old_locus_tag = utils.optionally(six.string_types)
    operon = utils.optionally(six.string_types)
    standard_name = utils.optionally(six.string_types)
    description = utils.optionally(six.string_types)
    mol_type = utils.optionally(six.string_types)
    is_composite = utils.optionally(six.string_types)
    pseudogene = utils.optionally(six.string_types)

    location_start = utils.optionally(six.integer_types)
    location_end = utils.optionally(six.integer_types)

    gene_synonyms = utils.possibly_empty(list)
    references = utils.possibly_empty(list)

    secondary_structure = utils.possibly_empty(SecondaryStructure)

    @property
    def database_name(self):
        """
        Get the database name in upper case.
        """
        return self.database.upper()  # pylint: disable=E1101

    @property
    def exons(self):
        exons = []
        for region in self.regions:
            exons.extend(region.exons)
        return exons

    @property
    def db_xrefs(self):
        """
        Return a JSON encoded dict representing the xref data.
        """
        return json.dumps(self.xref_data)

    @property
    def note(self):
        """
        Return a JSON encoded dictionary representing the note data.
        """
        return json.dumps(self.note_data)

    @property
    def feature_name(self):
        """
        Return the feature for the RNA type.
        """
        if self.rna_type in FEATURE_TYPE_RNAS:
            return self.rna_type
        return 'ncRNA'

    @property
    def ncrna_class(self):
        """
        The ncRNA class. If the feature type is not ncRNA this this will be the
        empty string.
        """
        if self.feature_name != 'ncRNA':
            return None
        return self.rna_type

    @property
    def gene_synonym(self):
        """
        Returns a comma separated list of gene synonyms.
        """
        return ','.join(self.gene_synonyms)

    @property
    def feature_location_start(self):
        """
        This will compute the feature location start if it is not set,
        otherwise this will use the set one.
        """

        if self.location_start is not None:
            return self.location_start
        if not self.exons:
            return 1
        return min(e.start for e in self.exons)

    @property
    def feature_location_end(self):
        """
        This will compute the feature location end if it is not set,
        otherwise this will use the set one.
        """

        if self.location_end is not None:
            return self.location_end
        if not self.exons:
            return len(self.sequence) + 1
        return max(e.stop for e in self.exons)

    def crc64(self):
        """
        Compute a CRC64 check sum for the sequence.
        """
        return crc64(self.sequence)

    def md5(self):
        """
        Compute an MD5 hash of the sequence.
        """
        return md5(self.sequence)

    def is_valid(self):
        """
        Detect if this entry is valid. This means it is neither too short (< 10
        nt) not too long (> 1000000 nts) and has less than 10% N's.
        """

        length = len(self.sequence)
        if length < 10:
            LOGGER.warn("%s is too short (%s)", self.accession, length)
            return False

        if length > 1000000:
            LOGGER.warn("%s is too long (%s)", self.accession, length)
            return False

        counts = Counter(self.sequence)
        fraction = float(counts.get('N', 0)) / float(len(self.sequence))
        if fraction > 0.1:
            LOGGER.warn(
                "%s has too many (%i/%i) N's",
                self.accession,
                counts['N'],
                length
            )
            return False

        return True

    def write_ac_info(self):
        if not self.is_valid():
            return
        yield [
            self.accession,
            self.parent_accession,
            self.seq_version,
            self.feature_location_start,
            self.feature_location_end,
            self.feature_name,
            self.ordinal,
            self.is_composite,
            self.non_coding_id,
            self.database_name,
            self.primary_id,
            self.optional_id,
            self.project,
            None,  # self.division,
            self.keywords,
            self.description,
            self.species,
            self.common_name,
            self.organelle,
            self.lineage,
            None,  # This was self.allele,
            self.anticodon,
            self.chromosome,
            self.experiment,
            self.function,
            self.gene,
            self.gene_synonym,
            self.inference,
            self.locus_tag,
            None,  # This was self.map,
            self.mol_type,
            self.ncrna_class,
            self.note,
            self.old_locus_tag,
            self.operon,
            self.product,
            self.pseudogene,
            self.standard_name,
            self.db_xrefs,
            # self.rna_type,
        ]

    def write_secondary_structure(self):
        if not self.is_valid():
            return []
        # pylint: disable=no-member
        return self.secondary_structure.writeable(self.accession)

    def write_sequence(self):
        if not self.is_valid():
            return
        yield [
            self.crc64(),
            len(self.sequence),
            self.sequence,
            self.database_name,
            self.accession,
            self.optional_id,
            self.seq_version,
            self.ncbi_tax_id,
            self.md5(),
        ]

    def write_seq_short(self):
        if len(self.sequence) <= 4000:
            return self.write_sequence()
        return []

    def write_seq_long(self):
        if len(self.sequence) > 4000:
            return self.write_sequence()
        return []

    def write_refs(self):
        refs = six.moves.filter(lambda r: isinstance(r, Reference), self.references)
        return self.__write_part__(refs)

    def write_ref_ids(self):
        refs = self.references
        refs = six.moves.filter(lambda r: isinstance(r, IdReference), refs)
        return self.__write_part__(refs)

    def write_genomic_locations(self):
        return self.__write_part__(self.regions, method_name='writeable_exons')

    def write_related_sequences(self):
        return self.__write_part__(self.related_sequences)

    def write_sequence_features(self):
        for related in self.related_sequences:
            features = related.write_features(self.accession, self.ncbi_tax_id)
            for feature in features:
                yield feature

    def write_sequence_regions(self):
        return self.__write_part__(self.regions)

    def __write_part__(self, attribute, method_name='writeable'):
        if not self.is_valid():
            return []
        method = op.methodcaller(method_name, self.accession)
        writeable = six.moves.map(method, attribute)
        return it.chain.from_iterable(writeable)
