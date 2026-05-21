# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import math
import os
from typing import Dict, List, Optional

import yaml
from nmp.evaluator.app.values import EvaluationResult, GroupResult, TaskResult
from pydantic import TypeAdapter

log = logging.getLogger(__name__)


def load_evaluation_result(job_id: str, results_filepath: str, name: str, workspace: str) -> EvaluationResult:
    if not os.path.isfile(results_filepath):
        raise FileNotFoundError(f"No evaluation results file '{results_filepath}' from evaluation step")

    # Read evaluation results file
    with open(results_filepath, "r") as file:
        if results_filepath.endswith("json"):
            results = json.load(file)
        elif results_filepath.endswith("yaml") or results_filepath.endswith("yml"):
            results = yaml.safe_load(file)
        else:
            raise ValueError(f"Unsupported results file {results_filepath}!")

    # Convert results / handle any discrepancies
    tasks: Optional[Dict[str, TaskResult]] = None
    result_tasks = results.get("tasks") or results.get("results", {}).get("tasks")
    if result_tasks:
        filtered_task_results = filter_empty_scores(result_tasks)
        tasks = TypeAdapter(Optional[Dict[str, TaskResult]]).validate_python(filtered_task_results)
    else:
        log.warning("Tasks are missing in results of the job %s.", job_id)

    groups: Optional[Dict[str, GroupResult]] = None
    result_groups = results.get("groups") or results.get("results", {}).get("groups")
    if result_groups:
        filtered_group_results = filter_empty_scores(result_groups)
        groups = TypeAdapter(Optional[Dict[str, GroupResult]]).validate_python(filtered_group_results)
    else:
        log.warning("Groups are missing in results of the job %s.", job_id)

    return EvaluationResult(workspace=workspace, job=job_id, tasks=tasks, groups=groups)


def no_metrics(evaluation_result: EvaluationResult) -> bool:
    """Traverse results to see if no metric is populated"""
    if not (evaluation_result.tasks or evaluation_result.groups):
        return True

    if evaluation_result.tasks:
        for task in evaluation_result.tasks.values():
            if not task.metrics:
                continue
            for metric in task.metrics.values():
                if metric.scores:
                    return False

    if evaluation_result.groups:
        for group in evaluation_result.groups.values():
            if not group.metrics:
                continue
            for metric in group.metrics.values():
                if metric.scores:
                    return False
    return True


def _extract_nan_metrics(items: Dict) -> List[str]:
    """Helper function to extract NaN metrics from tasks or groups.

    Args:
        items: Dictionary of tasks or groups

    Returns:
        List of metric identifiers that contain NaN values
    """
    nan_metrics: List[str] = []

    for item_name, item in items.items():
        if not item.metrics:
            continue
        for metric_name, metric in item.metrics.items():
            if not metric.scores:
                continue
            for score_name, score in metric.scores.items():
                if not (hasattr(score, "value") and score.value is not None):
                    continue
                if math.isnan(score.value):
                    nan_metrics.append(f"{item_name}.{metric_name}.{score_name}")

    return nan_metrics


def nan_metrics_present(evaluation_result: EvaluationResult) -> List[str]:
    """Traverse results to identify metrics with NaN values.

    Returns:
        List of metric names that contain NaN values. Empty list if no NaN values found.
    """
    nan_metrics: List[str] = []

    if evaluation_result.tasks:
        nan_metrics.extend(_extract_nan_metrics(evaluation_result.tasks))

    if evaluation_result.groups:
        nan_metrics.extend(_extract_nan_metrics(evaluation_result.groups))

    return nan_metrics


def filter_empty_scores(task_results: dict) -> dict:
    filtered: dict = {}

    if task_results:
        for task_name, task_result in task_results.items():
            filtered_metrics: dict = {}

            if task_result.get("metrics"):
                for metric_name, metric_result in task_result["metrics"].items():
                    filtered_scores = {}

                    if metric_result.get("scores"):
                        for score_name, score in metric_result["scores"].items():
                            if score.get("value") is not None:
                                filtered_scores[score_name] = score

                    metric_result["scores"] = filtered_scores

                    if metric_result["scores"]:
                        filtered_metrics[metric_name] = metric_result

            if filtered_metrics:
                task_result["metrics"] = filtered_metrics

            if task_result:
                filtered[task_name] = task_result

    return filtered
