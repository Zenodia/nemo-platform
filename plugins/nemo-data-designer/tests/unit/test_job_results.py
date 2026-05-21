# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest
from nemo_data_designer_plugin.sdk.errors import (
    DataDesignerClientError,
    DataDesignerJobError,
)
from nemo_data_designer_plugin.sdk.job_results import DataDesignerJobResults


def test_load_analysis_success(tmp_path: Path) -> None:
    mock_analysis = Mock()
    results = DataDesignerJobResults(artifacts_dir=tmp_path, analysis=mock_analysis)
    assert results.load_analysis() is mock_analysis


def test_load_analysis_raises_when_error_string(tmp_path: Path) -> None:
    error_msg = "Unable to fetch analysis: something went wrong"
    results = DataDesignerJobResults(artifacts_dir=tmp_path, analysis=error_msg)
    with pytest.raises(DataDesignerJobError, match=error_msg):
        results.load_analysis()


def test_load_dataset(tmp_path: Path) -> None:
    parquet_files_dir = tmp_path / "dataset" / "parquet-files"
    parquet_files_dir.mkdir(parents=True)

    expected_df = pd.DataFrame({"col": [1, 2, 3]}).convert_dtypes(dtype_backend="pyarrow")
    expected_df.to_parquet(f"{parquet_files_dir}/00000.parquet", index=False)

    results = DataDesignerJobResults(artifacts_dir=tmp_path, analysis=Mock())

    dataset = results.load_dataset()
    pd.testing.assert_frame_equal(dataset, expected_df)


def test_load_processor_dataset(tmp_path: Path) -> None:
    processor_name = "chat_format"

    processor_files_dir = tmp_path / "dataset" / "processors-files" / processor_name
    processor_files_dir.mkdir(parents=True)

    expected_df = pd.DataFrame({"col": [1, 2, 3]}).convert_dtypes(dtype_backend="pyarrow")
    expected_df.to_parquet(f"{processor_files_dir}/00000.parquet", index=False)

    results = DataDesignerJobResults(artifacts_dir=tmp_path, analysis=Mock())

    dataset = results.load_processor_dataset(processor_name)
    pd.testing.assert_frame_equal(dataset, expected_df)

    with pytest.raises(DataDesignerClientError):
        results.load_processor_dataset("undefined-processor")
