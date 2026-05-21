# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PreparedResults:
    aggregate_scores_path: str
    row_scores_path: str | None


class ResultsParser(Protocol):
    def prepare_results(self, local_results_dir_path: str) -> PreparedResults:
        """Prepare normalized result artifacts and return their paths."""
        ...
