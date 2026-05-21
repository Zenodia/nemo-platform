# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Configuration for the Evaluator plugin.

Demonstrates the :class:`~nemo_platform_plugin.config.NemoConfig` pattern: declare
:attr:`plugin_name` and :attr:`plugin_description` as ``ClassVar`` strings, then
add plugin-specific fields as regular Pydantic fields.

Operators set values via environment variables or the Helm ``platformConfig`` key:

    # Environment variables (highest priority)
    NMP_EVALUATOR_GREETING_STYLE=casual

    # Helm values.yaml (platformConfig key)
    platformConfig:
      evaluator:
        greeting_style: casual
"""

from __future__ import annotations

from typing import ClassVar, Literal

from nemo_platform_plugin.config import NemoConfig
from pydantic import Field


class EvaluatorConfig(NemoConfig):
    """Configuration for the NeMo Platform evaluator plugin.

    All fields have defaults so the plugin runs out-of-the-box without any
    operator configuration.  Override via environment variables or the Helm
    ``platformConfig.evaluator`` section.
    """

    plugin_name: ClassVar[str] = "evaluator"
    plugin_description: ClassVar[str] = "Configuration for the NeMo Platform evaluator plugin."

    greeting_style: Literal["formal", "casual"] = Field(
        default="formal",
        description=(
            "Controls the tone of /hello/{name} responses. "
            '"formal" → "Hello, {name}!"  "casual" → "Hey, {name}!"'
            "  Set NMP_EVALUATOR_GREETING_STYLE to override."
        ),
    )
