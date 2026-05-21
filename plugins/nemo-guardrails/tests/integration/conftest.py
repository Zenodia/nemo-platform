# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Pytest fixtures for the guardrails plugin integration tests.

Re-exports the IGW harness fixtures so test modules don't have to import
them at the top of every file, and provides an autouse fixture that
keeps ``nemoguardrails`` from reaching out to HuggingFace at startup.

- :func:`igw_plugin_harness` — default; no real port for IGW.
- :func:`igw_loopback_harness` — opt-in; IGW additionally bound on a real
  ``127.0.0.1:<port>`` for tests that need IGW's loopback URL. Call it with
  extra services to mount additional routes.
"""

import pytest
from nmp.core.inference_gateway.testing.fixtures import igw_loopback_harness, igw_plugin_harness

__all__ = ["igw_loopback_harness", "igw_plugin_harness"]


@pytest.fixture(autouse=True)
def offline_huggingface(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip ``nemoguardrails`` HuggingFace tokenizer downloads — they time out offline."""
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
