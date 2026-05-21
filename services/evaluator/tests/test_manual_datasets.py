# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import sys

import pytest
from nmp.common.files.deprecated_datastore.datasets import Dataset
from nmp.evaluator.app.datasets.nmp_datasets import load_dataset
from pydantic import AnyUrl

TEST_DATA_ROOT = os.path.join(os.path.dirname(__file__), "datasets")

is_manual = any("test_manual" in arg for arg in sys.argv)


@pytest.mark.asyncio
@pytest.mark.skipif(not is_manual, reason="Only run manually")
async def test_load_local_file_dataset():
    dataset = await load_dataset(Dataset(files_url=AnyUrl(f"file://{TEST_DATA_ROOT}/math/simple-math.csv")))
    assert len(dataset) == 3

    dataset = await load_dataset(Dataset(files_url=AnyUrl(f"file://{TEST_DATA_ROOT}/qa/questions.json")))
    assert len(dataset) == 4


@pytest.mark.asyncio
@pytest.mark.skipif(not is_manual, reason="Only run manually")
async def test_load_local_folder_dataset():
    dataset = await load_dataset(Dataset(files_url=AnyUrl(f"file://{TEST_DATA_ROOT}/math")))
    assert len(dataset) == 3

    dataset = await load_dataset(Dataset(files_url=AnyUrl(f"file://{TEST_DATA_ROOT}/qa")))
    assert len(dataset) == 4


@pytest.mark.skipif(not is_manual, reason="Only run manually")
@pytest.mark.asyncio
async def test_load_datastore_dataset():
    os.environ["DATA_STORE_URL"] = "http://data-store.test:8008/v1/hf"

    dataset = await load_dataset(Dataset(files_url=AnyUrl("hf://datasets/default/eval-test-data-math")))
    assert len(dataset) == 3


@pytest.mark.skipif(not is_manual, reason="Only run manually")
@pytest.mark.asyncio
async def test_load_datastore_file():
    os.environ["DATA_STORE_URL"] = "http://data-store.test:8008/v1/hf"

    dataset = await load_dataset(Dataset(files_url=AnyUrl("hf://datasets/default/eval-test-data-math/simple-math.csv")))
    assert len(dataset) == 3


@pytest.mark.skipif(not is_manual, reason="Only run manually")
@pytest.mark.asyncio
async def test_load_datastore_file_with_limit():
    os.environ["DATA_STORE_URL"] = "http://data-store.test:8008/v1/hf"

    dataset = await load_dataset(
        Dataset(files_url=AnyUrl("hf://datasets/default/eval-test-data-math/simple-math.csv"), limit=1)
    )
    assert len(dataset) == 1


@pytest.mark.skipif(not is_manual, reason="Only run manually")
@pytest.mark.asyncio
async def test_load_hugging_face_hub_dataset():
    dataset = await load_dataset(
        Dataset(
            files_url=AnyUrl("hf://datasets/cornell-movie-review-data/rotten_tomatoes"),
            hf_endpoint=AnyUrl("https://huggingface.co"),
        )
    )
    assert len(dataset) == 8530
