# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import math
from typing import Dict, Optional

import pytest
from nmp.evaluator.app.jobs.results import filter_empty_scores, nan_metrics_present, no_metrics
from nmp.evaluator.app.values import (
    DeprecatedMetricResult,
    DeprecatedScoreValue,
    EvaluationResult,
    GroupResult,
    TaskResult,
)
from pydantic import TypeAdapter


def test_filter_empty_scores():
    input = {
        "task1": {
            "metrics": {
                "metric with no scores": {},
                "metric with valid score": {"scores": {"Overall Acc": {"value": 1.15, "stats": None}}},
                "metric with scores filtered": {
                    "scores": {
                        "Overall Acc": {"value": 1.15, "stats": None},
                        "score to be filtered out": {
                            "value": None,
                            "stats": None,
                        },
                    }
                },
            }
        },
        "task2": {
            "metrics": {
                "metric with score to be filtered out": {
                    "scores": {
                        "score to be filtered out": {
                            "value": None,
                            "stats": None,
                        }
                    }
                },
                "metric to be kept": {"scores": {"Overall Acc": {"value": 1.15, "stats": None}}},
            }
        },
        "task3": {
            "metrics": {
                "metric with no scores": {},
                "metric to be kept": {"scores": {"Overall Acc": {"value": 1.15, "stats": None}}},
            }
        },
        "task4": {"metrics": {}},
    }

    filtered = filter_empty_scores(input)

    expected = {
        "task1": {
            "metrics": {
                "metric with valid score": {"scores": {"Overall Acc": {"value": 1.15, "stats": None}}},
                "metric with scores filtered": {"scores": {"Overall Acc": {"value": 1.15, "stats": None}}},
            }
        },
        "task2": {"metrics": {"metric to be kept": {"scores": {"Overall Acc": {"value": 1.15, "stats": None}}}}},
        "task3": {"metrics": {"metric to be kept": {"scores": {"Overall Acc": {"value": 1.15, "stats": None}}}}},
        "task4": {"metrics": {}},
    }

    assert expected == filtered


@pytest.mark.parametrize(
    "evaluation_result, expected, description",
    [
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={
                    "task": TaskResult(
                        metrics={
                            "my-task-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=0.1)}
                            )
                        }
                    )
                },
            ),
            False,
            "one task metric",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={
                    "task": TaskResult(
                        metrics={
                            "my-task-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=0.1)}
                            ),
                            "my-task-metric2": DeprecatedMetricResult(
                                scores={"my-score2": DeprecatedScoreValue(value=0.5)}
                            ),
                        }
                    )
                },
            ),
            False,
            "multiple task metrics",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                groups={
                    "group": GroupResult(
                        metrics={
                            "my-group-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=0.1)}
                            )
                        }
                    )
                },
            ),
            False,
            "one group metric",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                groups={
                    "group": GroupResult(
                        metrics={
                            "my-group-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=0.1)}
                            ),
                            "my-group-metric2": DeprecatedMetricResult(
                                scores={"my-score2": DeprecatedScoreValue(value=0.5)}
                            ),
                        }
                    )
                },
            ),
            False,
            "multiple group metrics",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={
                    "task": TaskResult(
                        metrics={
                            "my-task-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=0.1)}
                            ),
                            "my-task-metric2": DeprecatedMetricResult(
                                scores={"my-score2": DeprecatedScoreValue(value=0.5)}
                            ),
                        }
                    )
                },
                groups={
                    "group": GroupResult(
                        metrics={
                            "my-group-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=0.1)}
                            ),
                            "my-group-metric2": DeprecatedMetricResult(
                                scores={"my-score2": DeprecatedScoreValue(value=0.5)}
                            ),
                        }
                    )
                },
            ),
            False,
            "task and group metrics",
        ),
        (EvaluationResult(workspace="default", job="job-id"), True, "empty result"),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={"task": TaskResult(metrics={})},
                groups={"group": GroupResult(metrics={})},
            ),
            True,
            "empty metric",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={
                    "task": TaskResult(
                        metrics={
                            "my-task-metric": DeprecatedMetricResult(scores={"my-score": DeprecatedScoreValue(value=0)})
                        }
                    )
                },
                groups={
                    "group": GroupResult(
                        metrics={
                            "my-group-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=0)}
                            )
                        }
                    )
                },
            ),
            False,
            "empty scores",
        ),
    ],
)
def test_no_metrics(evaluation_result: EvaluationResult, expected: bool, description: str):
    raw_result: dict = evaluation_result.model_dump()
    if evaluation_result.tasks:
        filtered_task_results = filter_empty_scores(raw_result["tasks"])
        evaluation_result.tasks = TypeAdapter(Optional[Dict[str, TaskResult]]).validate_python(filtered_task_results)
    if evaluation_result.groups:
        filtered_group_results = filter_empty_scores(raw_result["groups"])
        evaluation_result.groups = TypeAdapter(Optional[Dict[str, GroupResult]]).validate_python(filtered_group_results)
    assert no_metrics(evaluation_result) is expected, description


@pytest.mark.parametrize(
    "evaluation_result, expected, description",
    [
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={
                    "task": TaskResult(
                        metrics={
                            "my-task-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=0.1)}
                            )
                        }
                    )
                },
            ),
            [],
            "no NaN values in task metrics",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={
                    "task": TaskResult(
                        metrics={
                            "my-task-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=math.nan)}
                            )
                        }
                    )
                },
            ),
            ["task.my-task-metric.my-score"],
            "NaN value in task metric",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={
                    "task1": TaskResult(
                        metrics={
                            "metric1": DeprecatedMetricResult(scores={"score1": DeprecatedScoreValue(value=math.nan)})
                        }
                    ),
                    "task2": TaskResult(
                        metrics={
                            "metric2": DeprecatedMetricResult(scores={"score2": DeprecatedScoreValue(value=math.nan)})
                        }
                    ),
                },
            ),
            ["task1.metric1.score1", "task2.metric2.score2"],
            "NaN values in multiple task metrics",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                groups={
                    "group": GroupResult(
                        metrics={
                            "my-group-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=math.nan)}
                            )
                        }
                    )
                },
            ),
            ["group.my-group-metric.my-score"],
            "NaN value in group metric",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={
                    "task": TaskResult(
                        metrics={
                            "my-task-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=math.nan)}
                            )
                        }
                    )
                },
                groups={
                    "group": GroupResult(
                        metrics={
                            "my-group-metric": DeprecatedMetricResult(
                                scores={"my-score": DeprecatedScoreValue(value=math.nan)}
                            )
                        }
                    )
                },
            ),
            ["task.my-task-metric.my-score", "group.my-group-metric.my-score"],
            "NaN values in both task and group metrics",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={
                    "task": TaskResult(
                        metrics={
                            "metric1": DeprecatedMetricResult(scores={"score1": DeprecatedScoreValue(value=0.5)}),
                            "metric2": DeprecatedMetricResult(scores={"score2": DeprecatedScoreValue(value=math.nan)}),
                        }
                    )
                },
            ),
            ["task.metric2.score2"],
            "mixed valid and NaN values in task metrics",
        ),
        (
            EvaluationResult(workspace="default", job="job-id"),
            [],
            "empty result - no NaN values",
        ),
        (
            EvaluationResult(
                workspace="default",
                job="job-id",
                tasks={"task": TaskResult(metrics={})},
                groups={"group": GroupResult(metrics={})},
            ),
            [],
            "empty metrics - no NaN values",
        ),
    ],
)
def test_nan_metrics_present(evaluation_result: EvaluationResult, expected: list, description: str):
    result = nan_metrics_present(evaluation_result)
    assert result == expected, description
