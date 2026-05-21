# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""MiddlewareRegistry — route inbound requests to per-model Switchyard chains.

Stores a static mapping of model name → :class:`Switchyard`.  The launcher
populates the registry at startup after building all chains from factory
configuration.  The three V2 HTTP endpoints read ``body["model"]``, call
:meth:`lookup_switchyard`, and dispatch to the returned chain before making any
backend calls.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from switchyard.lib.switchyard import Switchyard

log = logging.getLogger(__name__)


class MiddlewareRegistry:
    """Registry that maps model names to pre-built :class:`Switchyard` chains.

    Register one chain per model the proxy should handle explicitly. Unknown
    models raise ``KeyError`` so endpoint handlers can return ``model_not_found``
    instead of silently forwarding a request to the wrong backend.
    """

    #: Same key as :class:`Switchyard` so app factories store this under the
    #: attribute the V2 endpoint handlers already read.
    state_key: ClassVar[str] = "switchyard"

    def __init__(self) -> None:
        self._by_model: dict[str, Switchyard] = {}
        self._metadata_by_model: dict[str, dict[str, Any]] = {}

    def register(
        self,
        model: str,
        switchyard: Switchyard,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        """Register *switchyard* as the exact-match chain for *model*."""
        self._by_model[model] = switchyard
        self._metadata_by_model[model] = dict(metadata or {})
        log.debug("MiddlewareRegistry: registered chain for model=%r", model)

    def registered_models(self) -> list[str]:
        """Return registered model ids in registration order."""
        return list(self._by_model)

    def lookup_switchyard(self, model: str) -> Switchyard:
        """Return the chain for *model*.

        Raises:
            KeyError: *model* is unregistered.
        """
        chain = self._by_model.get(model)
        if chain is not None:
            log.debug("MiddlewareRegistry: model=%r → registered chain", model)
            return chain
        raise KeyError(model)

    def registered_model_entries(self) -> list[dict[str, Any]]:
        """Return OpenAI-compatible model entries with optional metadata."""
        entries: list[dict[str, Any]] = []
        for model in self._by_model:
            metadata = dict(self._metadata_by_model.get(model, {}))
            display_name = metadata.pop("display_name", model)
            metadata.pop("id", None)
            metadata.pop("object", None)
            metadata.pop("type", None)
            entry: dict[str, Any] = {
                "id": model,
                "object": "model",
                "type": "model",
                "display_name": display_name,
            }
            entry.update(metadata)
            entries.append(entry)
        return entries

    def iter_components(self) -> list[Any]:
        """Return all chain components across registered chains, deduplicated.

        Components shared by object identity are returned once so endpoint and
        shutdown hooks are not double-registered.
        """
        seen: set[int] = set()
        result: list[Any] = []
        for switchyard in self._by_model.values():
            for component in switchyard.iter_components():
                if id(component) in seen:
                    continue
                seen.add(id(component))
                result.append(component)
        return result
