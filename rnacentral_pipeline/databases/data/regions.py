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


class UnkonwnCoordianteSystemName(Exception):
    pass


def sort_exons(exons):
    return tuple(sorted(exons, key=op.attrgetter('start')))


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


@enum.unique
class CoordianteStart(enum.Enum):
    zero = 0
    one = 1


@enum.unique
class CloseStatus(enum.Enum):
    closed = 0
    open = 1


@attr.s(frozen=True, hash=True, slots=True)
class CoordinateSystem(object):
    """
    This is meant to represent how a database numbers a genome. Some databases
    will start counting at zeros and others one, this is called the basis here.
    If the stop endpoint is open or closed changes the value of the close_status
    here.
    """

    basis = attr.ib(validator=is_a(CoordianteStart))
    close_status = attr.ib(validator=is_a(CloseStatus))

    @classmethod
    def from_name(cls, name):
        if name == '0-start, half-open':
            return cls(basis=CoordianteStart.zero, close_status=CloseStatus.open)
        if name == "1-start, fully-closed":
            return cls(basis=CoordianteStart.one, close_status=CloseStatus.closed)
        raise UnkonwnCoordianteSystemName(name)

    @classmethod
    def zero_based(cls):
        return cls(basis=CoordianteStart.zero, close_status=CloseStatus.open)

    @classmethod
    def one_based(cls):
        return cls(basis=CoordianteStart.one, close_status=CloseStatus.closed)

    def name(self):
        if self.basis is CoordianteStart.zero and \
                self.close_status is CloseStatus.open:
            return '0-start, half-open'
        if self.basis is CoordianteStart.one and \
                self.close_status is CloseStatus.closed:
            return "1-start, fully-closed"
        raise ValueError("No name for %s" % self)

    def length(self, location):
        pass
        # if self.as_one_based():
        #     return self.stop - location.start + 1
        # if self.is_zero_based():
        #     return self.stop - location.start

    def as_zero_based(self, location):
        pass

    def as_one_based(self, location):
        start = location.start
        stop = location.stop
        if self.basis is CoordianteStart.zero:
            start = start + 1
        elif self.basis is CoordianteStart.one:
            pass
        else:
            raise ValueError("Unknown type of start: %s" % self.basis)

        if self.close_status is CloseStatus.closed:
            pass
        elif self.close_status is CloseStatus.open:
            stop = stop - 1
        else:
            raise ValueError("Unknown type of shift: %s" % self.shift)

        return attr.evolve(location, start=start, stop=stop)

    def normalize(self, location):
        return as_one_based(location)


@attr.s(frozen=True, hash=True, slots=True)
class Exon(object):
    start = attr.ib(validator=is_a(six.integer_types))
    stop = attr.ib(validator=is_a(six.integer_types))

    @classmethod
    def from_dict(cls, raw):
        return cls(start=raw['exon_start'], stop=raw['exon_stop'])


@attr.s(frozen=True, hash=True, slots=True)
class SequenceRegion(object):
    assembly_id = attr.ib(validator=is_a(six.text_type))
    chromosome = attr.ib(validator=is_a(six.text_type))
    strand = attr.ib(validator=is_a(Strand), converter=Strand.build)
    exons = attr.ib(validator=is_a(tuple), converter=sort_exons)
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

    def lengths(self):
        return [self.coordinate_system.length(e) for e in self.exons]

    def as_one_based(self):
        coverter = self.coordinate_system.as_one_based
        return attr.evolve(
            self,
            exons=[converter(e) for e in self.exons],
            coordinate_system=CoordinateSystem.one_based(),
        )

    def as_zero_based(self):
        coverter = self.coordinate_system.as_zero_based
        return attr.evolve(
            self,
            exons=[converter(e) for e in self.exons],
            coordinate_system=CoordinateSystem.zero_based(),
        )

    def writeable(self, accession, upi=False, require_strand=True):
        if require_strand and self.strand is Strand.unknown:
            return

        name = self.name()
        if upi:
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
