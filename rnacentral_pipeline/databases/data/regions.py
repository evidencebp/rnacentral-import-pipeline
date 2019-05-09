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

import operator as op

import six

import enum

import attr
from attr.validators import instance_of as is_a


class UnknownStrand(Exception):
    """
    Raised when a strand integer has an invalid value.
    """
    pass


class UnknownCoordinateStart(Exception):
    pass


class UnknownCloseStatus(Exception):
    pass


class UnknownCoordinateSystem(Exception):
    pass


@enum.unique
class Strand(enum.Enum):
    reverse = -1
    unknown = 0
    forward = 1

    @classmethod
    def build(cls, value):
        if isinstance(value, float) and int(value) == value:
            value = int(value)
        if value in {1, '+', '1', Strand.forward}:
            return cls.forward
        if value in {-1, '-', '-1', Strand.reverse}:
            return cls.reverse
        if value in {0, '.', 0, Strand.unknown}:
            return cls.unknown
        raise UnknownStrand("No way to handle raw strand: " + six.text_type(value))

    def display_string(self):
        if self is Strand.reverse:
            return '-'
        if self is Strand.forward:
            return '+'
        if self is Strand.unknown:
            return '.'
        raise ValueError("Strand %s has no representation" % self)

    def display_int(self):
        return self.value


# @enum.unique
class CoordianteStart(enum.Enum):
    zero = 0
    one = 1

    @classmethod
    def from_name(cls, name):
        if name == '0-start':
            return cls.zero
        if name == '1-start':
            return cls.one
        raise UnknownCoordinateStart(name)

    def __str__(self):
        return '%i-start' % self.value


# @enum.unique
class CloseStatus(enum.Enum):
    closed = 0
    open = 1

    @classmethod
    def from_name(cls, name):
        if name == 'fully-closed':
            return cls.closed
        if name == 'half-open':
            return cls.open
        raise UnknownCloseStatus(name)

    def __str__(self):
        if self is CloseStatus.closed:
            return 'fully-closed'
        if self is CloseStatus.open:
            return 'half-open'
        raise ValueError("No name for %s" % self)


@attr.s(frozen=True, hash=True, slots=True)
class CoordinateSystem(object):
    """
    This is meant to represent how a database numbers a genome. Some databases
    will start counting at zeros and others one, this is called the basis here.
    If the stop endpoint is open or closed changes the value of the close_status
    here. This is really only meant to cover the two main systems 0 based and
    1 based. The logic of how to represent things and deal with the two systems
    is taken from:

    http://genome.ucsc.edu/blog/the-ucsc-genome-browser-coordinate-counting-systems/
    """

    basis = attr.ib(validator=is_a(CoordianteStart))
    close_status = attr.ib(validator=is_a(CloseStatus))

    @classmethod
    def from_name(cls, name):
        """
        Create a CoordinateSystem from a given name. The name must be formatted
        like 'basis, close_status'. Examples are: 

        - '0-start, half-open', 
        - '1-start, fully-closed'
        """

        try:
            basis_name, close_name = name.split(', ', 1)
        except:
            raise UnknownCoordinateSystem(name)

        return cls(
            basis=CoordianteStart.from_name(basis_name),
            close_status=CloseStatus.from_name(close_name),
        )

    @classmethod
    def zero_based(cls):
        """
        Just a short cut for '0-start, half-open'.
        """
        return cls.from_name('0-start, half-open')

    @classmethod
    def one_based(cls):
        """
        Just a short cut for '1-start, fully-closed'.
        """
        return cls.from_name("1-start, fully-closed")

    def name(self):
        return '%s, %s' % (self.basis, self.close_status)

    def size(self, location):
        size = None
        if self.close_status == CloseStatus.closed:
            size = location.stop - location.start + 1
        elif self.close_status == CloseStatus.open:
            size = location.stop - location.start
        else:
            raise ValueError("Could not find the size for %s" % location)

        assert size >= 0, "Somehow computed negative exon size %s" % location
        return size

    def as_zero_based(self, location):
        start = location.start
        if self.basis is CoordianteStart.zero:
            pass
        elif self.basis is CoordianteStart.one:
            start = start - 1
        else:
            raise ValueError("Unknown type of start: %s" % self.basis)

        return attr.evolve(location, start=start)

    def as_one_based(self, location):
        start = location.start
        if self.basis is CoordianteStart.zero:
            start = start + 1
        elif self.basis is CoordianteStart.one:
            pass
        else:
            raise ValueError("Unknown type of start: %s" % self.basis)

        return attr.evolve(location, start=start)

    def normalize(self, location):
        return self.as_one_based(location)


@attr.s(frozen=True, hash=True, slots=True)
class Exon(object):
    start = attr.ib(validator=is_a(six.integer_types))
    stop = attr.ib(validator=is_a(six.integer_types))

    @classmethod
    def from_dict(cls, raw):
        return cls(start=raw['exon_start'], stop=raw['exon_stop'])

    @stop.validator
    def greater_than_start(self, attribute, value):
        if value < self.start:
            raise ValueError("stop (%i) must be >= start (%i)" % 
                             (value, self.start))


@attr.s(frozen=True, hash=True, slots=True)
class SequenceRegion(object):
    assembly_id = attr.ib(validator=is_a(six.text_type), converter=six.text_type)
    chromosome = attr.ib(validator=is_a(six.text_type), converter=six.text_type)
    strand = attr.ib(validator=is_a(Strand), converter=Strand.build)
    exons = attr.ib(
        validator=is_a(tuple), 
        converter=lambda es: tuple(sorted(es, key=op.attrgetter('start'))),
    )
    coordinate_system = attr.ib(validator=is_a(CoordinateSystem))

    @property
    def start(self):
        return self.exons[0].start

    @property
    def stop(self):
        return self.exons[-1].stop

    def name(self, upi=''):
        exon_names = []
        for exon in self.exons:
            normalized = self.coordinate_system.normalize(exon)
            exon_names.append('{start}-{stop}'.format(
                start=normalized.start,
                stop=normalized.stop,
            ))

        return '{upi}@{chromosome}/{exons}:{strand}'.format(
            upi=upi,
            chromosome=self.chromosome,
            exons=','.join(exon_names),
            strand=self.strand.display_string(),
        )

    def sizes(self):
        return [self.coordinate_system.size(e) for e in self.exons]

    def as_one_based(self):
        converter = self.coordinate_system.as_one_based
        return attr.evolve(
            self,
            exons=[converter(e) for e in self.exons],
            coordinate_system=CoordinateSystem.one_based(),
        )

    def as_zero_based(self):
        converter = self.coordinate_system.as_zero_based
        return attr.evolve(
            self,
            exons=[converter(e) for e in self.exons],
            coordinate_system=CoordinateSystem.zero_based(),
        )

    def writeable(self, accession, is_upi=False, require_strand=True):
        assert accession, 'Must given an accession to write %s' % self
        if require_strand and self.strand is Strand.unknown:
            return

        name = self.name()
        if is_upi:
            name = self.name(upi=accession)

        for exon in self.exons:
            normalized = self.coordinate_system.normalize(exon)
            yield [
                accession,
                name,
                self.chromosome,
                self.strand.display_int(),
                self.assembly_id,
                len(self.exons),
                normalized.start,
                normalized.stop,
            ]
