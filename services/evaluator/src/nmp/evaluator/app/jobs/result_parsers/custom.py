# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os

from nmp.evaluator.app.jobs.constants import (
    EVALUATION_RESULTS_AGG_SCORES_FILE_NAME,
    EVALUATION_RESULTS_ROW_SCORES_FILE_NAME,
)
from nmp.evaluator.app.jobs.result_parsers.base import PreparedResults, ResultsParser


class CustomResultsParser(ResultsParser):
    def prepare_results(self, local_results_dir_path: str) -> PreparedResults:
        aggregate_scores_path = os.path.join(local_results_dir_path, EVALUATION_RESULTS_AGG_SCORES_FILE_NAME)
        if not os.path.isfile(aggregate_scores_path):
            raise FileNotFoundError(
                f"No custom evaluation results file '{EVALUATION_RESULTS_AGG_SCORES_FILE_NAME}' "
                f"found in {local_results_dir_path}"
            )

        row_scores_path = os.path.join(local_results_dir_path, EVALUATION_RESULTS_ROW_SCORES_FILE_NAME)
        if not os.path.isfile(row_scores_path):
            with open(row_scores_path, "w"):
                pass
        return PreparedResults(
            aggregate_scores_path=aggregate_scores_path,
            row_scores_path=row_scores_path,
        )
