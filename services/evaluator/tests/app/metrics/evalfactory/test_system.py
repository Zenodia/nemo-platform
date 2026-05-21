# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from nmp.evaluator.app.evalfactory.retriever import RetrieverHandler
from nmp.evaluator.app.evalfactory.system import (
    AgenticEvalHandler,
    BigCodeEvaluationHarnessHandler,
    SafetyHarnessHandler,
    SystemMetricsHandler,
    get_system_benchmark_handler,
    get_system_metric,
    get_system_metric_handler,
)
from nmp.evaluator.app.values import SystemMetric


@pytest.mark.parametrize(
    "metric_name,expected",
    [
        ("trajectory-evaluation", AgenticEvalHandler._system_metrics[0]),
        ("retriever-map", RetrieverHandler._system_metrics[0]),
    ],
)
def test_get_system_metric(metric_name: str, expected: SystemMetric):
    metric = get_system_metric(metric_name)
    assert metric.name == metric_name
    assert metric == expected


def test_get_system_metric_not_found():
    with pytest.raises(ValueError, match="Unknown system metric"):
        get_system_metric("dne")


@pytest.mark.parametrize(
    "metric_name,expected",
    [
        ("trajectory-evaluation", AgenticEvalHandler),
        ("retriever-map", RetrieverHandler),
    ],
)
def test_get_system_metric_handler(metric_name: str, expected: type[SystemMetricsHandler]):
    handler = get_system_metric_handler(metric_name)
    assert isinstance(handler, expected)


def test_get_system_metric_handler_not_found():
    with pytest.raises(ValueError, match="Unknown system metric"):
        get_system_metric_handler("bfclv3-simple")


@pytest.mark.parametrize(
    "metric_name,expected",
    [
        ("humaneval", BigCodeEvaluationHarnessHandler),
        ("aegis-v2", SafetyHarnessHandler),
    ],
)
def test_get_system_benchmark_handler(metric_name: str, expected: type[SystemMetricsHandler]):
    handler = get_system_benchmark_handler(metric_name)
    assert isinstance(handler, expected)


def test_get_system_benchmark_handler_not_found():
    with pytest.raises(ValueError, match="Unknown system benchmark"):
        get_system_benchmark_handler("dne")
