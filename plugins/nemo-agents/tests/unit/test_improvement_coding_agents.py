# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the improvement/coding_agents/ submodule."""

from __future__ import annotations

import pytest
from nemo_agents_plugin.improvement.coding_agents.base import CodingAgent, InvocationResult
from nemo_agents_plugin.improvement.coding_agents.claude import ClaudeCodingAgent


def test_claude_implements_coding_agent_protocol() -> None:
    agent = ClaudeCodingAgent()
    assert isinstance(agent, CodingAgent)
    assert agent.name == "claude"


def test_invocation_result_default() -> None:
    r = InvocationResult()
    assert r.changed_files == []
    assert r.explanation == ""
    assert r.returncode == 0


def test_claude_preflight_raises_when_claude_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """When `claude` isn't on PATH, preflight should raise a clear error."""
    monkeypatch.setattr("shutil.which", lambda cmd: None)
    agent = ClaudeCodingAgent()
    with pytest.raises(RuntimeError, match="Coding agent 'claude' not found"):
        agent.preflight()
