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

import itertools as it
import json
import operator as op
import typing as ty

import attr
from attr.validators import instance_of as is_a
from attr.validators import optional

from rnacentral_pipeline.databases.data import regions


def lookup_databases(raw):
    lookup = {
        "ENA": "ENA",
        "RFAM": "Rfam",
        "SRPDB": "SRPDB",
        "MIRBASE": "miRBase",
        "VEGA": "VEGA",
        "TMRNA_WEB": "tmRNA Website",
        "LNCRNADB": "lncRNAdb",
        "GTRNADB": "GtRNAdb",
        "REFSEQ": "RefSeq",
        "RDP": "RDP",
        "PDBE": "PDBe",
        "SNOPY": "snOPY",
        "GREENGENES": "Greengenes",
        "TAIR": "TAIR",
        "WORMBASE": "WormBase",
        "SGD": "SGD",
        "SILVA": "SILVA",
        "POMBASE": "PomBase",
        "DICTYBASE": "dictyBase",
        "LNCIPEDIA": "LNCipedia",
        "NONCODE": "NONCODE",
        "MODOMICS": "Modomics",
        "HGNC": "HGNC",
        "FLYBASE": "FlyBase",
        "ENSEMBL": "Ensembl",
        "GENCODE": "GENCODE",
        "MGI": "MGI",
        "RGD": "RGD",
        "TARBASE": "TarBase",
        "ZWD": "ZWD",
        "ENSEMBL_PLANTS": "Ensembl Plants",
        "LNCBASE": "LncBase",
        "LNCBOOK": "LncBook",
        "ENSEMBL_METAZOA": "Ensembl Metazoa",
        "ENSEMBL_PROTISTS": "Ensembl Protists",
        "ENSEMBL_FUNGI": "Ensembl Fungi",
        "SNODB": "snoDB",
        "5SRRNADB": "5SrRNAdb",
        "MIRGENEDB": "MirGeneDB",
        "MALACARDS": "MalaCards",
        "GENECARDS": "GeneCards",
        "INTACT": "IntAct",
        "SNORNADB": "snoRNA Database",
        "ZFIN": "ZFIN",
        "CRW": "CRW",
        "PIRBASE": "piRBase",
        "ENSEMBL_GENCODE": "Ensembl/GENCODE",
        "PSICQUIC": "PSICQUIC",
        "RIBOVISION": "RiboVision",
        "PLNCDB": "PLncDB",
        "EXPRESSION_ATLAS": "Expression Atlas",
        "RIBOCENTRE": "Ribocentre",
        "EVLNCRNAS": "EVLncRNAs",
        "REDIPORTAL": "REDIPortal",
        "MGNIFY": "MGnify",
    }
    return [lookup[d] for d in raw]


def clean_databases(raw):
    return [d.replace(" ", "_") for d in raw]


@attr.s(hash=True, slots=True, frozen=True)
class Region(object):
    region_id = attr.ib(validator=is_a(str), converter=str)
    rna_id = attr.ib(validator=is_a(str), converter=str)
    region = attr.ib(validator=is_a(regions.SequenceRegion))
    was_mapped = attr.ib(validator=is_a(bool))
    identity = attr.ib(
        validator=optional(is_a(float)),
        default=None,
        cmp=False,
    )
    metadata = attr.ib(validator=is_a(dict), default=dict, cmp=False)

    @classmethod
    def build(cls, index, raw):
        identity = None
        if raw["identity"] is not None:
            identity = float(raw["identity"])

        exons = []
        for exon in raw["exons"]:
            exons.append(
                regions.Exon(
                    start=exon["exon_start"],
                    stop=exon["exon_stop"],
                )
            )

        region_id = "{rna_id}.{index}".format(rna_id=raw["rna_id"], index=index)

        metadata = {
            "description": raw["description"],
            "rna_type": raw["rna_type"],
            "providing_databases": lookup_databases(raw["providing_databases"]),
            "databases": clean_databases(raw["databases"]),
        }
        if not metadata["providing_databases"]:
            del metadata["providing_databases"]

        return cls(
            region_id=region_id,
            rna_id=raw["rna_id"],
            region=regions.SequenceRegion(
                assembly_id=raw["assembly_id"],
                chromosome=raw["chromosome"],
                strand=raw["strand"],
                exons=exons,
                coordinate_system=regions.CoordinateSystem.one_based(),
            ),
            identity=identity,
            was_mapped=raw["was_mapped"],
            metadata=metadata,
        )

    @property
    def start(self):
        return self.region.start

    @property
    def stop(self):
        return self.region.stop

    @property
    def chromosome(self):
        return self.region.chromosome

    @property
    def exons(self):
        return self.region.exons

    @property
    def source(self):
        if self.was_mapped:
            return "alignment"
        return "expert-database"

    def string_strand(self):
        return self.region.strand.display_string()

    def as_one_based(self):
        return attr.evolve(self, region=self.region.as_one_based())

    def as_zero_based(self):
        return attr.evolve(self, region=self.region.as_zero_based())


def parse(regions) -> ty.Iterable[Region]:
    for index, region in enumerate(regions):
        yield Region.build(index, region)


def from_file(handle) -> ty.Iterable[Region]:
    data = map(json.loads, handle)
    data = filter(lambda d: d["rna_type"] != "NULL", data)
    yield from parse(data)
