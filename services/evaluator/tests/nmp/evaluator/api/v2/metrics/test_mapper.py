# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for MetricMapper."""

from unittest.mock import AsyncMock, patch

import nmp.evaluator.entities as entities
import pytest
from nemo_evaluator_sdk.enums import ModelFormat
from nemo_evaluator_sdk.metrics.llm_judge import default_judge_prompt_template_chat
from nemo_evaluator_sdk.values import Model, Rubric, RubricScore
from nmp.evaluator.api.v2.metrics.mapper import MetricMapper
from nmp.evaluator.api.v2.metrics.schemas import metrics as schemas
from nmp.evaluator.app.values.common import ModelRef


class TestMetricMapperRequestToEntity:
    """Tests for MetricMapper.request_to_entity method."""

    @pytest.mark.asyncio
    async def test_request_to_entity_llm_judge(self):
        """Test converting LLMJudgeMetric to LLMJudgeMetric entity."""
        # Arrange
        request = schemas.LLMJudgeMetric(
            description="Test LLM Judge metric",
            model=Model(
                url="https://api.openai.com/v1",
                name="gpt-4o",
                format=ModelFormat.OPEN_AI,
            ),
            prompt_template="Rate the response: {output}",
            scores=[
                RubricScore(
                    name="quality",
                    description="Quality of response",
                    rubric=[
                        Rubric(label="good", description="Good response", value=1),
                        Rubric(label="bad", description="Bad response", value=0),
                    ],
                )
            ],
        )

        # Act
        entity = await MetricMapper.request_to_entity(request, name="test-metric", workspace="default")

        # Assert
        assert isinstance(entity, entities.LLMJudgeMetric)
        assert entity.name == "test-metric"
        assert entity.workspace == "default"
        assert entity.description == "Test LLM Judge metric"
        assert entity.model.name == "gpt-4o"

    @pytest.mark.asyncio
    async def test_request_to_entity_bleu(self):
        """Test converting BLEUMetric to BLEUMetric entity."""
        # Arrange
        request = schemas.BLEUMetric(
            references=["{{item.reference}}"],
        )

        # Act
        entity = await MetricMapper.request_to_entity(request, name="test-bleu", workspace="default")

        # Assert
        assert isinstance(entity, entities.BLEUMetric)
        assert entity.name == "test-bleu"
        assert entity.workspace == "default"
        assert entity.type == "bleu"
        assert entity.references == ["{{item.reference}}"]

    @pytest.mark.asyncio
    async def test_request_to_entity_rouge(self):
        """Test converting ROUGEMetric to ROUGEMetric entity."""
        # Arrange
        request = schemas.ROUGEMetric(
            reference="{{item.reference}}",
        )

        # Act
        entity = await MetricMapper.request_to_entity(request, name="test-rouge", workspace="test-workspace")

        # Assert
        assert isinstance(entity, entities.ROUGEMetric)
        assert entity.name == "test-rouge"
        assert entity.workspace == "test-workspace"
        assert entity.type == "rouge"

    @pytest.mark.asyncio
    async def test_request_to_entity_string_check(self):
        """Test converting StringCheckMetric to StringCheckMetric entity."""
        # Arrange
        request = schemas.StringCheckMetric(
            operation="contains",
            left_template="{{item.response}}",
            right_template="{{item.expected}}",
        )

        # Act
        entity = await MetricMapper.request_to_entity(request, name="test-string-check", workspace="default")

        # Assert
        assert isinstance(entity, entities.StringCheckMetric)
        assert entity.name == "test-string-check"
        assert entity.workspace == "default"
        assert entity.type == "string-check"
        assert entity.operation == "contains"

    @pytest.mark.asyncio
    async def test_request_to_entity_preserves_all_fields(self):
        """Test that all fields from the request are preserved in the entity."""
        # Arrange
        request = schemas.BLEUMetric(
            references=["{{item.reference1}}", "{{item.reference2}}"],
            candidate="{{item.candidate}}",
        )

        # Act
        entity = await MetricMapper.request_to_entity(request, name="test-bleu", workspace="default")

        # Assert
        assert isinstance(entity, entities.BLEUMetric)
        assert entity.references == ["{{item.reference1}}", "{{item.reference2}}"]
        assert entity.candidate == "{{item.candidate}}"

    @pytest.mark.asyncio
    async def test_request_to_entity_ragas_with_judge_model(self):
        """Test converting RAGAS metric with judge_model to entity."""
        # Arrange - TopicAdherence is a RAGAS metric with judge_model
        request = schemas.TopicAdherenceMetric(
            judge_model=Model(
                url="https://api.openai.com/v1",
                name="gpt-4o",
                format=ModelFormat.OPEN_AI,
            ),
        )

        # Act
        entity = await MetricMapper.request_to_entity(request, name="test-topic", workspace="default")

        # Assert
        assert isinstance(entity, entities.TopicAdherenceMetric)
        assert entity.name == "test-topic"
        assert entity.workspace == "default"
        assert entity.type == "topic_adherence"
        assert entity.judge_model.name == "gpt-4o"

    @pytest.mark.asyncio
    async def test_request_to_entity_response_relevancy_both_models(self):
        """Test ResponseRelevancy which has both judge_model and embeddings_model."""
        # Arrange - ResponseRelevancy is unique in having both judge and embeddings models
        request = schemas.ResponseRelevancyMetric(
            judge_model=Model(
                url="https://api.openai.com/v1",
                name="gpt-4o",
                format=ModelFormat.OPEN_AI,
            ),
            embeddings_model=Model(
                url="https://api.openai.com/v1",
                name="text-embedding-3-small",
                format=ModelFormat.OPEN_AI,
            ),
        )

        # Act
        entity = await MetricMapper.request_to_entity(request, name="test-relevancy", workspace="default")

        # Assert
        assert isinstance(entity, entities.ResponseRelevancyMetric)
        assert entity.name == "test-relevancy"
        assert entity.workspace == "default"
        assert entity.type == "response_relevancy"
        assert entity.judge_model.name == "gpt-4o"
        assert entity.embeddings_model.name == "text-embedding-3-small"

    @pytest.mark.asyncio
    async def test_request_to_entity_resolves_model_ref(self):
        """Test that ModelRef fields are resolved via the ResolvableModels protocol."""
        # Arrange - TopicAdherence with a ModelRef instead of inline Model
        # Use the API schema type which accepts Model | ModelRef
        request = schemas.TopicAdherenceMetric.model_validate({"judge_model": ModelRef(root="my-workspace/my-judge")})

        resolved_model = Model(
            url="http://gateway:8080/v1/my-workspace/my-judge",
            name="my-judge",
            format=ModelFormat.NVIDIA_NIM,
        )

        # Act - mock resolve_model which is called by the ResolvableModels protocol
        with patch(
            "nmp.evaluator.api.v2.metrics.mapper.resolve_model",
            new_callable=AsyncMock,
            return_value=resolved_model,
        ):
            entity = await MetricMapper.request_to_entity(request, name="test-topic", workspace="default")

        # Assert - entity should have the resolved app.Model
        assert isinstance(entity, entities.TopicAdherenceMetric)
        assert entity.judge_model.name == "my-judge"
        assert entity.judge_model.url == "http://gateway:8080/v1/my-workspace/my-judge"
        assert entity.judge_model.format == "nim"

    @pytest.mark.asyncio
    async def test_request_to_entity_resolves_multiple_model_refs(self):
        """Test that multiple ModelRef fields are all resolved."""
        # Arrange - ResponseRelevancy has both judge_model and embeddings_model
        # Use the API schema type which accepts Model | ModelRef
        request = schemas.ResponseRelevancyMetric.model_validate(
            {
                "judge_model": ModelRef(root="ws/judge"),
                "embeddings_model": ModelRef(root="ws/embed"),
            }
        )

        async def fake_resolve(model):
            if isinstance(model, ModelRef) and "judge" in model.root:
                return Model(url="http://gw/v1/ws/judge", name="judge", format=ModelFormat.NVIDIA_NIM)
            if isinstance(model, ModelRef) and "embed" in model.root:
                return Model(url="http://gw/v1/ws/embed", name="embed", format=ModelFormat.NVIDIA_NIM)
            return model

        with patch(
            "nmp.evaluator.api.v2.metrics.mapper.resolve_model",
            side_effect=fake_resolve,
        ):
            entity = await MetricMapper.request_to_entity(request, name="test-rel", workspace="default")

        assert isinstance(entity, entities.ResponseRelevancyMetric)
        assert entity.judge_model.name == "judge"
        assert entity.embeddings_model.name == "embed"

    @pytest.mark.asyncio
    async def test_request_to_entity_llm_judge_defaults_prompt_template_when_omitted(self):
        """LLM Judge should support zero-config prompt templates."""
        request = schemas.LLMJudgeMetric(
            model=Model(
                url="https://inference-api.nvidia.com/v1/chat/completions",
                name="nvidia/openai/gpt-oss-20b",
                format=ModelFormat.OPEN_AI,
            ),
            scores=[
                RubricScore(
                    name="quality",
                    rubric=[
                        Rubric(label="poor", value=0),
                        Rubric(label="good", value=1),
                    ],
                )
            ],
        )
        assert request.prompt_template == default_judge_prompt_template_chat()

        entity = await MetricMapper.request_to_entity(request, name="test-judge", workspace="default")

        assert isinstance(entity, entities.LLMJudgeMetric)
        assert entity.prompt_template == default_judge_prompt_template_chat()

    @pytest.mark.asyncio
    async def test_request_to_entity_llm_judge_preserves_optional_fields(self):
        request = schemas.LLMJudgeMetric(
            model=Model(
                url="https://inference-api.nvidia.com/v1/chat/completions",
                name="nvidia/openai/gpt-oss-20b",
                format=ModelFormat.OPEN_AI,
            ),
            optional_fields=["reference"],
            scores=[
                RubricScore(
                    name="quality",
                    rubric=[
                        Rubric(label="poor", value=0),
                        Rubric(label="good", value=1),
                    ],
                )
            ],
        )

        entity = await MetricMapper.request_to_entity(request, name="test-judge", workspace="default")

        assert isinstance(entity, entities.LLMJudgeMetric)
        assert entity.optional_fields == ["reference"]
