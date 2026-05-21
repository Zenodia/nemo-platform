# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Dataset-related value types."""

from __future__ import annotations

from typing import Annotated, Any, Literal, get_args

from nemo_evaluator_sdk.values import DatasetRows
from nmp.evaluator.app.values.common import Fileset, FilesetRef
from pydantic import BeforeValidator, RootModel

# Define the strictly allowed dataset identifiers
# This includes the 22 BEIR datasets and the 1 Ragas dataset
# Known BEIR academic datasets are downloaded from https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/
# and RAGAS amnesty_qa downloaded from huggingface.

BuiltInDatasetID = Literal[
    "beir/climate-fever",
    "beir/cqadupstack",
    "beir/dbpedia-entity",
    "beir/fever",
    "beir/fiqa",
    "beir/germanquad",
    "beir/hotpotqa",
    "beir/mmarco",
    "beir/mrtydi",
    "beir/msmarco-v2",
    "beir/msmarco",
    "beir/nfcorpus",
    "beir/nq-train",
    "beir/nq",
    "beir/quora",
    "beir/scidocs",
    "beir/scifact",
    "beir/trec-covid-beir",
    "beir/trec-covid-v2",
    "beir/trec-covid",
    "beir/vihealthqa",
    "beir/webis-touche2020",
    "ragas/amnesty_qa",
]


class BuiltInDataset(RootModel):
    """Well-known dataset (BEIR or RAGAS) referenced by its identifier."""

    root: BuiltInDatasetID

    @property
    def format(self) -> str:
        """Extracts the format (e.g., 'beir' or 'ragas').

        If there's no slash in the identifier, returns an empty string.
        """
        parts = self.root.split("/")
        return parts[0] if len(parts) > 1 else ""

    @property
    def name(self) -> str:
        """Extracts the dataset name (e.g., 'fiqa' or 'amnesty_qa').

        If there's no slash in the identifier, returns the entire root string.
        """
        parts = self.root.split("/")
        return parts[1] if len(parts) > 1 else self.root


def _coerce_string_to_fileset_ref(v: Any) -> Any:
    """Convert plain strings to FilesetRef for proper deserialization.

    When a FilesetRef is serialized to JSON, it becomes a plain string.
    This validator ensures that plain strings are parsed back as FilesetRef
    when validating a Dataset union type.
    """
    if isinstance(v, str):
        return FilesetRef(root=v)
    return v


Dataset = Annotated[DatasetRows | FilesetRef | Fileset, BeforeValidator(_coerce_string_to_fileset_ref)]


def _coerce_string_to_pipeline_dataset(v: Any) -> Any:
    """Convert plain strings to FilesetRef or BuiltInDataset for proper deserialization.

    When a FilesetRef is serialized to JSON, it becomes a plain string.
    This validator ensures that plain strings are parsed back as FilesetRef
    when validating a PipelineDataset union type. BuiltInDataset identifiers (e.g., "beir/fiqa")
    are recognized and converted to BuiltInDataset instead.
    """
    if isinstance(v, str):
        # Check if string matches a known built-in dataset identifier
        if v in get_args(BuiltInDatasetID):
            return BuiltInDataset(root=v)
        return FilesetRef(root=v)
    return v


# BuiltInDataset must come first so strings like "beir/fiqa" are validated
# against it before Dataset's BeforeValidator converts them to FilesetRef.
PipelineDataset = Annotated[BuiltInDataset | Dataset, BeforeValidator(_coerce_string_to_pipeline_dataset)]
