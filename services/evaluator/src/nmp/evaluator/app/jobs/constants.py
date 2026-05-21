# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Literal, cast, get_args

# Used as the env name to serialize EvalFactory YAML configuration
# whereas NEMO_JOB_STEP_CONFIG expects JSON
NEMO_EVAL_FACTORY_JOB_CONFIG = "NEMO_EVAL_FACTORY_JOB_CONFIG"
NEMO_EVAL_HARNESS = "NEMO_EVAL_HARNESS"
EVALUATOR_HARNESS = "evaluator"
EvalHarness = Literal[
    "evaluator",
    "retriever",
    "agentic_eval",
    "safety_harness",
    "simple_evals",
    "lm_eval_harness",
    "bigcode_eval_harness",
    "bfcl",
]
VALID_EVAL_HARNESSES = frozenset(get_args(EvalHarness))

# File name of the EvalFactory configuration
EVALFACTORY_EVALUATION_JOB_FILE_NAME = "evaluation_job_file.yaml"

# Results file names - match the result entity names for consistency
EVALUATION_RESULTS_AGG_SCORES_FILE_NAME = "aggregate-scores.json"
EVALUATION_RESULTS_ROW_SCORES_FILE_NAME = "row-scores.jsonl"

# Results file name from EvalFactory
EVALFACTORY_EVALUATION_RESULTS_AGG_SCORES_FILE_NAME = "results.yml"

JOBS_RESULTS_ARTIFACTS = "artifacts"  # archived job directory
JOB_RESULTS_AGGREGATE_SCORES = "aggregate-scores"  # aggregated scores
JOB_RESULTS_ROW_SCORES = "row-scores"  # per-row scores


def resolve_eval_harness(labels: dict | None) -> EvalHarness:
    if isinstance(labels, dict) and isinstance(labels.get("eval_harness"), str):
        return normalize_eval_harness(labels["eval_harness"])
    return EVALUATOR_HARNESS


def normalize_eval_harness(eval_harness: str | None) -> EvalHarness:
    normalized = (
        eval_harness.strip().lower() if isinstance(eval_harness, str) and eval_harness.strip() else EVALUATOR_HARNESS
    )
    if normalized not in VALID_EVAL_HARNESSES:
        raise ValueError(f"Unsupported eval harness '{eval_harness}'. Expected one of: {sorted(VALID_EVAL_HARNESSES)}")
    return cast(EvalHarness, normalized)
