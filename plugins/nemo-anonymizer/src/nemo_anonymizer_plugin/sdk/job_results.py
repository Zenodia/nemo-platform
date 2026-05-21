# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Locally-loaded job results for the Anonymizer plugin SDK."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from nemo_anonymizer_plugin.sdk.display import DisplayRecordMixin, set_original_text_column
from nemo_anonymizer_plugin.sdk.errors import AnonymizerClientError


class AnonymizerJobResults(DisplayRecordMixin):
    """View into the artifacts saved by an Anonymizer run job.

    Layout (under ``artifacts/``):

      dataset.parquet          — user-facing dataframe (replace/rewrite output)
      trace.parquet            — internal trace dataframe with detection details
      failed_records.json      — records that failed during the pipeline
    """

    def __init__(self, artifacts_dir: Path):
        self._artifacts_dir = Path(artifacts_dir)
        self._display_cycle_index = 0

    def load_dataset(self) -> pd.DataFrame:
        path = self._artifacts_dir / "dataset.parquet"
        if not path.exists():
            raise AnonymizerClientError(f"Dataset artifact not found: {path}")
        return pd.read_parquet(path, dtype_backend="pyarrow")

    def load_trace(self) -> pd.DataFrame:
        path = self._artifacts_dir / "trace.parquet"
        if not path.exists():
            raise AnonymizerClientError(f"Trace artifact not found: {path}")
        trace = pd.read_parquet(path, dtype_backend="pyarrow")
        set_original_text_column(trace, self._load_metadata().get("original_text_column"))
        return trace

    def load_failed_records(self) -> list[dict]:
        path = self._artifacts_dir / "failed_records.json"
        if not path.exists():
            return []
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as exc:
            raise AnonymizerClientError(f"Invalid failed_records artifact: {path}") from exc

    def _display_trace_dataframe(self) -> pd.DataFrame:
        return self.load_trace()

    def _load_metadata(self) -> dict[str, str]:
        path = self._artifacts_dir / "metadata.json"
        if not path.exists():
            return {}
        try:
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError as exc:
            raise AnonymizerClientError(f"Invalid metadata artifact: {path}") from exc
        if not isinstance(raw, dict):
            raise AnonymizerClientError(f"Invalid metadata artifact: {path}")
        return {str(key): str(value) for key, value in raw.items() if isinstance(value, str)}
