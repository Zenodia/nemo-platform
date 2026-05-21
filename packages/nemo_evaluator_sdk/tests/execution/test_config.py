# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for nemo_evaluator_sdk.execution.config."""

from __future__ import annotations

import pytest
from nemo_evaluator_sdk.enums import AgentFormat
from nemo_evaluator_sdk.execution.config import EvaluationRequest
from nemo_evaluator_sdk.values import Agent, Model, RunConfigOnline, RunConfigOnlineModel


class TestEvaluationRequest:
    """Coverage for normalized request construction defaults."""

    @pytest.mark.parametrize(
        ("target", "expected_type"),
        [
            pytest.param(Model(url="http://example.test/v1", name="test-model"), RunConfigOnlineModel, id="model"),
            pytest.param(
                Agent(
                    url="http://agent.test",
                    name="test-agent",
                    format=AgentFormat.GENERIC,
                    body={"query": "{{ prompt }}"},
                    response_path="$.answer",
                ),
                RunConfigOnline,
                id="agent",
            ),
        ],
    )
    def test_defaults_target_specific_params(self, target: Model | Agent, expected_type: type[object]) -> None:
        """Omitted params should be normalized to the target-specific concrete type."""
        request = EvaluationRequest(dataset=[{"prompt": "a"}], target=target)

        assert isinstance(request.params, expected_type)

    def test_preserves_ignored_online_request_failure_params(self) -> None:
        """Request normalization should preserve params that control failure policy."""
        request = EvaluationRequest(
            dataset=[{"prompt": "a"}],
            params=RunConfigOnline(ignore_request_failure=True),
        )

        assert isinstance(request.params, RunConfigOnline)
        assert request.params.ignore_request_failure is True
        assert not hasattr(request, "fail_fast")
