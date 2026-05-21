# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""HTTP endpoint serving ``GET /v1/models`` for local model discovery."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from switchyard.lib.endpoints.base import Endpoint as NemoSwitchyardEndpoint
from switchyard.lib.middleware_registry import MiddlewareRegistry

if TYPE_CHECKING:
    from fastapi import FastAPI

log = logging.getLogger(__name__)


class ModelsEndpoint(NemoSwitchyardEndpoint):
    """Expose registered model ids for clients with model discovery."""

    def register(self, app: FastAPI) -> None:
        """Attach ``GET /v1/models`` onto *app*."""
        router = APIRouter()

        @router.get("/v1/models", response_model=None)
        async def models(request: Request) -> JSONResponse:
            obj = request.app.state.switchyard
            model_entries = (
                obj.registered_model_entries()
                if isinstance(obj, MiddlewareRegistry) else []
            )
            model_ids = [entry["id"] for entry in model_entries]
            log.debug("GET /v1/models returned %d model(s)", len(model_ids))
            return JSONResponse(content={
                "object": "list",
                "data": model_entries,
                "first_id": model_ids[0] if model_ids else None,
                "last_id": model_ids[-1] if model_ids else None,
                "has_more": False,
            })

        app.include_router(router, tags=["Model Discovery"])
