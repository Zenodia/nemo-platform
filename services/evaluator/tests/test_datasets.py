# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import tempfile

import pytest
from datasets import exceptions
from nmp.common.files.deprecated_datastore.datasets import Dataset
from nmp.evaluator.app.datasets.nmp_datasets.exceptions import UnsupportedFileFormatException
from nmp.evaluator.app.datasets.nmp_datasets.utils import (
    LoadingMode,
    _load_dataset_with_hf,
    _load_dataset_with_json,
    load_dataset,
)
from pydantic import AnyUrl


def test_load_dataset_with_hf_exception(mocker):
    mocker.patch(
        "nmp.evaluator.app.datasets.nmp_datasets.utils.hf_load_dataset"
    ).side_effect = exceptions.DatasetGenerationError
    mock_load_dataset_with_json = mocker.patch("nmp.evaluator.app.datasets.nmp_datasets.utils._load_dataset_with_json")

    _load_dataset_with_hf("some_path", None)

    mock_load_dataset_with_json.assert_called_with("some_path", None)


def test_load_dataset_with_hf_exception_file_path(mocker):
    mocker.patch(
        "nmp.evaluator.app.datasets.nmp_datasets.utils.hf_load_dataset"
    ).side_effect = exceptions.DatasetGenerationError
    mock_load_dataset_with_json = mocker.patch("nmp.evaluator.app.datasets.nmp_datasets.utils._load_dataset_with_json")

    _load_dataset_with_hf("some_path", "nested_dir_1/nested_dir_2/file.txt", "train")

    mock_load_dataset_with_json.assert_called_with("some_path", "nested_dir_1/nested_dir_2/file.txt")


def test_load_dataset_with_hf_exception_json_unsupported_format(mocker):
    mocker.patch(
        "nmp.evaluator.app.datasets.nmp_datasets.utils.hf_load_dataset"
    ).side_effect = exceptions.DatasetGenerationError
    mock_load_dataset_with_json = mocker.patch("nmp.evaluator.app.datasets.nmp_datasets.utils._load_dataset_with_json")
    mock_load_dataset_with_json.side_effect = UnsupportedFileFormatException

    with pytest.raises(UnsupportedFileFormatException):
        _load_dataset_with_hf("some_path", "nested_dir_1/nested_dir_2/file.txt")

    mock_load_dataset_with_json.assert_called_with("some_path", "nested_dir_1/nested_dir_2/file.txt")


def test_load_dataset_with_json_nested_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        json_file_name = "dataset_1.json"
        json_file_path = os.path.join(temp_dir, json_file_name)
        with open(json_file_path, "w") as json_file:
            json.dump([{"id": "row_1"}, {"id": "row_2"}], json_file)

        subpath = "subpath"
        os.mkdir(os.path.join(temp_dir, subpath))

        jsonl_file_name = "dataset_2.json"
        jsonl_file_path = os.path.join(temp_dir, subpath, jsonl_file_name)
        with open(jsonl_file_path, "w") as jsonl_file:
            jsonl_file.write(json.dumps({"id": "row_3"}))

        rows = _load_dataset_with_json(temp_dir, None)
        # Should have read 3 rows from 2 files
        assert len(rows) == 3


def test_load_dataset_with_json_nested_files_dir_load():
    with tempfile.TemporaryDirectory() as temp_dir:
        subpath = "subpath_1"
        dataset_path = os.path.join(temp_dir, subpath)
        os.mkdir(dataset_path)

        json_file_name = "dataset_1.json"
        json_file_path = os.path.join(temp_dir, subpath, json_file_name)
        with open(json_file_path, "w") as json_file:
            json.dump([{"id": "row_1"}, {"id": "row_2"}], json_file)

        subpath_1_1 = "subpath_1_1"
        os.mkdir(os.path.join(temp_dir, subpath, subpath_1_1))

        jsonl_file_name = "dataset_2.json"
        jsonl_file_path = os.path.join(temp_dir, subpath, subpath_1_1, jsonl_file_name)
        with open(jsonl_file_path, "w") as jsonl_file:
            jsonl_file.write(json.dumps({"id": "row_3"}))

        rows = _load_dataset_with_json(temp_dir, subpath)
        # Should have read 3 rows from 2 files
        assert len(rows) == 3


def test_load_dataset_with_json_unsupported_format_single_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        txt_file = "dataset.txt"
        file_path = os.path.join(temp_dir, txt_file)

        with open(file_path, "w"):
            with pytest.raises(UnsupportedFileFormatException):
                _load_dataset_with_json(temp_dir, txt_file)


def test_load_dataset_with_json_supported_format_with_other_unsupported():
    with tempfile.TemporaryDirectory() as temp_dir:
        json_file_name = "good_dataset.json"
        json_file_path = os.path.join(temp_dir, json_file_name)
        with open(json_file_path, "w") as json_file:
            json.dump([{"id": "row_1"}, {"id": "row_2"}], json_file)

        txt_file_name = "dataset.txt"
        txt_file_path = os.path.join(temp_dir, txt_file_name)
        with open(txt_file_path, "w"):
            pass

        rows = _load_dataset_with_json(temp_dir, json_file_name)
        assert len(rows) == 2


def test_load_dataset_with_json_unsupported_format_multiple_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        json_file = "good_dataset.json"
        json_file_path = os.path.join(temp_dir, json_file)
        with open(json_file_path, "w"):
            txt_file = "dataset.txt"
            txt_file_path = os.path.join(temp_dir, txt_file)
            with open(txt_file_path, "w"):
                with pytest.raises(UnsupportedFileFormatException):
                    _load_dataset_with_json(temp_dir, txt_file)


@pytest.mark.asyncio
async def test_load_dataset_limit():
    """
    Test loading dataset from file:// with limit
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        json_file_name = "dataset_1.json"
        json_file_path = os.path.join(temp_dir, json_file_name)
        with open(json_file_path, "w") as json_file:
            json.dump([{"id": "row_1"}, {"id": "row_2"}, {"id": "row_3"}], json_file)

        dataset = Dataset(files_url=AnyUrl(f"file://{json_file_path}"))
        loaded_dataset = await load_dataset(dataset, LoadingMode.SIMPLE)
        assert len(loaded_dataset) == 3, "expected all rows"

        dataset = Dataset(files_url=AnyUrl(f"file://{json_file_path}"), limit=2)
        loaded_dataset = await load_dataset(dataset, LoadingMode.SIMPLE)
        assert len(loaded_dataset) == 2, "expected limit to truncate dataset size"

        dataset = Dataset(files_url=AnyUrl(f"file://{json_file_path}"), limit=5)
        loaded_dataset = await load_dataset(dataset, LoadingMode.SIMPLE)
        assert len(loaded_dataset) == 3, "expected limit ignored when greater than dataset size"
