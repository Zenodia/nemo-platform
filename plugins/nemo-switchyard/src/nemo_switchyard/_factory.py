# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Switchyard factory class discovery and per-VM factory wrapper."""

from __future__ import annotations

import logging
from typing import Any

from nemo_switchyard._processors import PathUpdateProcessor

# Importing factories module triggers registration of Switchyard factories in the registry
from switchyard.lib import factories as _sy_factories  # noqa: F401
from switchyard.lib.factories.translate import TranslateFactory  # noqa: F401
from switchyard.lib.registry import lookup
from switchyard.lib.request_pipeline import RequestPipeline

logger = logging.getLogger(__name__)

# Map config_type to Switchyard factory CLASS (populated at on_startup)
CONFIG_TYPE_TO_FACTORY_CLASS: dict[str, Any] = {}

# user-facing config_type → Switchyard factory name in the registry. The IGW
# path uses only the request/response pipelines from each factory (the host
# owns the LLM backend), and Switchyard's unified factories put the routing
# decision in the request pipeline so IGW gets the routed model directly.
_CONFIG_TYPE_TO_SY_NAME: dict[str, str] = {
    "random_routing": "random_routing",
    "translate": "translate",
}


def initialize_factory_map() -> None:
    """Discover and map Switchyard factory classes by user-facing config_type."""
    for config_type, sy_name in _CONFIG_TYPE_TO_SY_NAME.items():
        try:
            factory_class = lookup(sy_name)
            CONFIG_TYPE_TO_FACTORY_CLASS[config_type] = factory_class
            logger.debug("Mapped config_type %r to factory class %r", config_type, sy_name)
        except Exception as e:
            logger.warning(
                "Failed to map config_type %r to factory %r: %s",
                config_type,
                sy_name,
                e,
                exc_info=True,
            )


class VMFactoryInstance:
    """Per-VM factory wrapper that holds a validated config.

    Registered in Switchyard's registry so processors/backends look up the right
    config-bound factory. Implements the MiddlewareFactory protocol by delegating
    to the wrapped factory class. For translate, appends PathUpdateProcessor to
    the request pipeline (path updates are translate-specific because translate
    is the only factory that converts between request formats with different
    API endpoints).

    Pipelines are built **once** at construction time and reused across requests.
    This is required for stateful processors like RandomRoutingRequestProcessor,
    whose RNG must persist across calls — rebuilding the pipeline per request
    re-seeds the RNG and produces the same routing decision every time.
    """

    def __init__(
        self,
        factory_class: Any,
        validated_config: Any,
        name: str,
        config_type: str = "",
    ) -> None:
        self.factory_class = factory_class
        self.config = validated_config
        self.name = name  # Required by Switchyard registry
        self.config_type = config_type
        # Copy class attributes from wrapped factory to satisfy MiddlewareFactory protocol
        self.config_class = getattr(factory_class, "config_class", None)

        # Build pipelines once so stateful processors (e.g. RNG in random_routing)
        # survive across requests instead of being reset on every call.
        base_request = self.factory_class.build_request_pipeline(self.config)
        if self.config_type == "translate":
            processors = list(base_request._processors) + [PathUpdateProcessor()]
            self._request_pipeline = RequestPipeline(processors)
        else:
            self._request_pipeline = base_request
        self._response_pipeline = self.factory_class.build_response_pipeline(self.config)

    def validate(self, raw: Any) -> Any:
        """Return the pre-validated config."""
        return self.config

    def build_request_pipeline(self, config: Any) -> Any:
        """Return the pre-built request pipeline."""
        return self._request_pipeline

    def build_response_pipeline(self, config: Any) -> Any:
        """Return the pre-built response pipeline."""
        return self._response_pipeline

    def build_backend(self, config: Any) -> Any:
        return self.factory_class.build_backend(self.config)

    def build_translator(self, config: Any) -> Any:
        return self.factory_class.build_translator(self.config)
