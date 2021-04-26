# -*- coding: utf-8 -*-

"""
Copyright [2009-2021] EMBL-European Bioinformatics Institute
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

import csv
import logging
import typing as ty
import operator as op
from pathlib import Path

import joblib
from more_itertools import chunked
import pandas as pd
from pypika import Table, Query, Order
import psycopg2
import psycopg2.extras
from sklearn.ensemble import RandomForestClassifier

from rnacentral_pipeline.rnacentral.r2dt import data

LOGGER = logging.getLogger(__name__)

MODEL_COLUMNS = [
    "source_index",
    "sequence_length",
    "diagram_sequence_length",
    "model_length",
    "model_basepair_count",
    "diagram_bps",
    "diagram_model_length",
    "diagram_overlap_count",
]


def fetch_modeled_data(
    all_ids: ty.Iterable[str], db_url: str, chunk_size=1000
) -> ty.Iterable[ty.Dict[str, ty.Any]]:
    rna = Table("rna")
    ss = Table("rnc_secondary_structure_layout")
    sm = Table("rnc_secondary_structure_layout_models")
    conn = psycopg2.connect(db_url)
    chunk_size = 100
    for chunk in chunked(all_ids, chunk_size):
        query = (
            Query.from_(rna)
            .select(
                rna.upi.as_("urs"),
                rna.len.as_("sequence_length"),
                sm.model_source,
                ss.sequence_start.as_("diagram_sequence_start"),
                ss.sequence_stop.as_("diagram_sequence_stop"),
                ss.basepair_count.as_("diagram_bps"),
                ss.model_start.as_("diagram_model_start"),
                ss.model_stop.as_("diagram_model_stop"),
                sm.model_length,
                sm.model_basepair_count,
                ss.overlap_count.as_("diagram_overlap_count"),
            )
            .join(ss)
            .on(ss.urs == rna.upi)
            .join(sm)
            .on(sm.id == ss.model_id)
            .where(ss.urs.isin(chunk))
        )

        seen: ty.Set[str] = set()
        sql = str(query)
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            for result in cur:
                yield result
                seen.add(result["urs"])

        missing = set(chunk) - seen
        for urs in missing:
            LOGGER.warn("Missed loading %s", urs)


def infer_columns(data: pd.DataFrame):
    data["diagram_sequence_length"] = data["diagram_sequence_stop"] - data["diagram_sequence_start"]
    data["diagram_model_length"] = data["diagram_model_stop"] - data["diagram_model_start"]


def fetch_training_data(handle: ty.IO, db_url: str) -> pd.DataFrame:
    ids = []
    data = {}
    for (urs, flag) in csv.reader(handle):
        ids.append(urs)
        if flag == "1":
            data[urs] = True
        elif flag == "0":
            data[urs] = False
        else:
            raise ValueError(f"Unknown flag {flag}")

    filled = []
    for metadata in fetch_modeled_data(ids, db_url):
        urs = metadata["urs"]
        if urs not in data:
            raise ValueError(f"Got an extra entry, somehow {metadata}")
        metadata["valid"] = data[urs]
        filled.append(metadata)

    data = pd.DataFrame.from_records(filled)
    infer_columns(data)
    return data


def train(handle, db_url) -> RandomForestClassifier:
    data = fetch_training_data(handle, db_url)
    X = data[MODEL_COLUMNS].to_numpy()
    y = data["vaild"].to_numpy()
    clf = RandomForestClassifier(min_samples_split=5)
    clf.fit(X, y)
    return clf


def parse(handle: ty.IO) -> ty.Iterable[data.ShowInfo]:
    for record in csv.DictReader(handle):
        yield data.ShowInfo.from_raw(record)


def write(model_path: Path, handle: ty.IO, output: ty.IO):
    model = joblib.load(model_path)
    data = pd.read_csv(handle)
    infer_columns(data)
    predicted = model.predict(data[MODEL_COLUMNS].to_numpy())
    to_write = pd.DataFrame()
    to_write['urs'] = data['urs']
    to_write['should_show'] = predicted
    to_write.to_csv(output, index=False)


def write_model(handle: ty.IO, db_url: str, output: Path):
    joblib.dump(train(handle, db_url), output)


def write_training_data(handle: ty.IO, db_url: str, output: ty.IO):
    ids = []
    for row in csv.reader(handle):
        ids.append(row[0])
    data = fetch_modeled_data(ids, db_url)
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
