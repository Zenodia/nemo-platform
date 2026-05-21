# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pandas as pd
from data_designer.config.analysis.dataset_profiler import DatasetProfilerResults
from data_designer.config.utils.io_helpers import read_parquet_dataset
from nemo_data_designer_plugin.sdk.errors import DataDesignerClientError, DataDesignerJobError


class DataDesignerJobResults:
    def __init__(self, artifacts_dir: Path, analysis: DatasetProfilerResults | str):
        self._artifacts_dir = artifacts_dir
        self._analysis = analysis

    def load_analysis(self) -> DatasetProfilerResults:
        if isinstance(self._analysis, str):
            raise DataDesignerJobError(self._analysis)

        return self._analysis

    def load_dataset(self) -> pd.DataFrame:
        dataset_path = self._artifacts_dir / "dataset" / "parquet-files"
        return read_parquet_dataset(dataset_path)

    def load_processor_dataset(self, processor_name: str) -> pd.DataFrame:
        dataset_path = self._artifacts_dir / "dataset" / "processors-files" / processor_name
        if not dataset_path.exists():
            raise DataDesignerClientError(f"No artifacts found for processor named {processor_name!r}")
        return read_parquet_dataset(dataset_path)
