# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Format translation :class:`MiddlewareFactory` for the IGW path.

Handles wire-format translation between inbound client format and the
target backend format. Decoupled from routing so Platform can compose
routing and translation independently.

The factory:
1. Stamps the original inbound format into context.
2. Translates the request to the target format (if different).
3. Translates the response back to the original format.

Configuration maps models to their target wire formats, allowing
per-model format heterogeneity (e.g., strong=Anthropic, weak=OpenAI).

Bundle shape:

| Slot              | TranslateFactory                     |
|-------------------| -------------------------------------|
| request_pipeline  | [Stamp, FormatTranslateReq]          |
| backend           | None (host owns it)                  |
| response_pipeline | [FormatTranslateResp]                |
| translator        | None (host owns it)                  |

Importing this module registers ``TranslateFactory`` under ``"translate"``
in the process-wide registry.
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from switchyard.lib.processors.format_translate import (
    FormatTranslateRequestProcessor,
    FormatTranslateResponseProcessor,
    StampOriginalFormatProcessor,
)
from switchyard.lib.registry import BaseMiddlewareFactory, register
from switchyard.lib.request_pipeline import RequestPipeline
from switchyard.lib.response_pipeline import ResponsePipeline


class TranslateConfig(BaseModel):
    """Configuration for :class:`TranslateFactory`.

    Maps each model name to its target wire format. When combined with
    routing middleware, the router picks a tier and stamps its target
    format into context; this factory then translates the request /
    response accordingly.

    Attributes:
        models: List of dicts mapping model names to backend formats.
            Each dict has ``model`` (str) and ``backend_format``
            (ChatRequestType enum string like "OPENAI_CHAT" or
            "ANTHROPIC_MESSAGES"). Can be empty if no translation
            is needed (request and response formats match).
    """

    model_config = ConfigDict(frozen=True)

    models: list[dict[str, str]] = []


class TranslateFactory(BaseMiddlewareFactory[TranslateConfig]):
    """Builds the format-translation processor pipeline for IGW hosts.

    Inherits ``return None`` defaults for :meth:`build_backend` and
    :meth:`build_translator` from :class:`BaseMiddlewareFactory` —
    IGW hosts supply both. The factory only contributes processors.
    """

    name: ClassVar[str] = "translate"
    config_class: ClassVar[type[BaseModel]] = TranslateConfig

    def validate(self, raw: Any) -> TranslateConfig:
        """Coerce a dict / Pydantic model into ``TranslateConfig``."""
        if isinstance(raw, TranslateConfig):
            return raw
        if isinstance(raw, BaseModel):
            return TranslateConfig(**raw.model_dump())
        if isinstance(raw, dict):
            return TranslateConfig(**raw)
        raise TypeError(
            f"TranslateFactory.validate() expected dict or "
            f"TranslateConfig, got {type(raw).__name__}"
        )

    def build_request_pipeline(
        self, config: TranslateConfig,
    ) -> RequestPipeline:
        """Build request pipeline: stamp original format, lookup target format, then translate."""
        from switchyard.lib.processors.format_translate import (
            ModelFormatLookupProcessor,
        )
        return RequestPipeline([
            StampOriginalFormatProcessor(),
            ModelFormatLookupProcessor(config),
            FormatTranslateRequestProcessor(),
        ])

    def build_response_pipeline(
        self, config: TranslateConfig,  # noqa: ARG002
    ) -> ResponsePipeline:
        """Build response pipeline: translate back to original format."""
        return ResponsePipeline([FormatTranslateResponseProcessor()])


register(TranslateFactory())
