# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from nemo_evaluator_sdk.enums import MetricType
from nemo_evaluator_sdk.metrics.ragas import (
    AgentGoalAccuracyMetric,
    AnswerAccuracyMetric,
    ContextEntityRecallMetric,
    ContextPrecisionMetric,
    ContextRecallMetric,
    ContextRelevanceMetric,
    FaithfulnessMetric,
    NoiseSensitivityMetric,
    ResponseGroundednessMetric,
    ResponseRelevancyMetric,
    ToolCallAccuracyMetric,
    TopicAdherenceMetric,
)
from nemo_evaluator_sdk.values import Model
from nmp.evaluator.app.metrics.metric import new_metric

MOCK_JUDGE_MODEL = Model(
    name="gpt-4",
    url="https://api.openai.com/v1",
)

MOCK_EMBEDDINGS_MODEL = Model(
    name="text-embedding-ada-002",
    url="https://api.openai.com/v1/embeddings",
)


@pytest.mark.parametrize(
    "metric_class,expected_type,extra_params",
    [
        (
            TopicAdherenceMetric,
            MetricType.TOPIC_ADHERENCE,
            {"metric_mode": "f1", "judge_model": MOCK_JUDGE_MODEL},
        ),
        (
            ToolCallAccuracyMetric,
            MetricType.TOOL_CALL_ACCURACY,
            {},
        ),
        (
            AgentGoalAccuracyMetric,
            MetricType.AGENT_GOAL_ACCURACY,
            {"use_reference": True, "judge_model": MOCK_JUDGE_MODEL},
        ),
        (
            AnswerAccuracyMetric,
            MetricType.ANSWER_ACCURACY,
            {"judge_model": MOCK_JUDGE_MODEL},
        ),
        (
            ContextRecallMetric,
            MetricType.CONTEXT_RECALL,
            {"judge_model": MOCK_JUDGE_MODEL},
        ),
        (
            ContextPrecisionMetric,
            MetricType.CONTEXT_PRECISION,
            {"judge_model": MOCK_JUDGE_MODEL},
        ),
        (
            ContextRelevanceMetric,
            MetricType.CONTEXT_RELEVANCE,
            {"judge_model": MOCK_JUDGE_MODEL},
        ),
        (
            ContextEntityRecallMetric,
            MetricType.CONTEXT_ENTITY_RECALL,
            {"judge_model": MOCK_JUDGE_MODEL},
        ),
        (
            ResponseGroundednessMetric,
            MetricType.RESPONSE_GROUNDEDNESS,
            {"judge_model": MOCK_JUDGE_MODEL},
        ),
        (
            ResponseRelevancyMetric,
            MetricType.RESPONSE_RELEVANCY,
            {"strictness": 1, "judge_model": MOCK_JUDGE_MODEL, "embeddings_model": MOCK_EMBEDDINGS_MODEL},
        ),
        (
            FaithfulnessMetric,
            MetricType.FAITHFULNESS,
            {"judge_model": MOCK_JUDGE_MODEL},
        ),
        (
            NoiseSensitivityMetric,
            MetricType.NOISE_SENSITIVITY,
            {"judge_model": MOCK_JUDGE_MODEL},
        ),
    ],
)
@pytest.mark.asyncio
async def test_new_metric_factory_all_ragas_metrics(metric_class, expected_type, extra_params):
    """Test that new_metric factory works for all RAGAS metric types."""
    # Create metric via factory
    metric = await new_metric(metric_class(**extra_params))

    # Verify type and instance
    assert isinstance(metric, metric_class)
    assert metric.type == expected_type


@pytest.mark.asyncio
async def test_new_metric_factory_invalid_type():
    """Test that new_metric raises error for unknown metric types."""
    from unittest.mock import MagicMock

    from nmp.evaluator.app.metrics.metric import new_metric

    # Create a mock config with an unknown metric type
    params = MagicMock()
    params.type = "unknown_metric_type"

    with pytest.raises(ValueError, match="Unknown metric type"):
        await new_metric(params)
