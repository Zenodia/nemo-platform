# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Middleware factory for the intake sink."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel

from switchyard.lib.factories.intake_sink.intake_sink_config import (
    IntakeSinkConfig,
)
from switchyard.lib.processors import IntakeRequestProcessor, IntakeResponseProcessor
from switchyard.lib.processors.intake_client import IntakeClient
from switchyard.lib.registry import BaseMiddlewareFactory, register
from switchyard.lib.request_pipeline import RequestPipeline
from switchyard.lib.response_pipeline import ResponsePipeline


class IntakeSinkFactory(BaseMiddlewareFactory[IntakeSinkConfig]):
    """Build the processor-only middleware bundle for Intake export."""

    name: ClassVar[str] = "intake_sink"
    config_class: ClassVar[type[BaseModel]] = IntakeSinkConfig

    def validate(self, raw: Any) -> IntakeSinkConfig:
        """Coerce a dict or Pydantic model into ``IntakeSinkConfig``."""
        if isinstance(raw, IntakeSinkConfig):
            return raw
        if isinstance(raw, BaseModel):
            return IntakeSinkConfig(**raw.model_dump())
        if isinstance(raw, dict):
            return IntakeSinkConfig(**raw)
        raise TypeError(
            "IntakeSinkFactory.validate() expected dict or IntakeSinkConfig, "
            f"got {type(raw).__name__}"
        )

    def build_request_pipeline(self, config: IntakeSinkConfig) -> RequestPipeline:
        return RequestPipeline([IntakeRequestProcessor()])

    def build_response_pipeline(self, config: IntakeSinkConfig) -> ResponsePipeline:
        client = IntakeClient(config)
        return ResponsePipeline([IntakeResponseProcessor(client.effective_config, client)])


register(IntakeSinkFactory())
