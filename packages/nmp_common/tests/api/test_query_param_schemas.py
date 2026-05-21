# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for register_query_param_schemas / clear_query_param_schemas.

These schemas are attached to FastAPI endpoints via ``openapi_extra`` and are
not reachable through Pydantic's response-model walk. The runtime
``custom_openapi`` hook has to call ``register_query_param_schemas`` explicitly
or the live ``/openapi.json`` will contain dangling ``$ref``s to the filter
classes.
"""

from typing import Optional

import pytest
from fastapi import FastAPI, Query, Request
from fastapi.openapi.utils import get_openapi
from fastapi.testclient import TestClient
from nmp.common.api.utils import (
    clear_query_param_schemas,
    generate_openapi_extra_params,
    register_query_param_schemas,
)
from pydantic import BaseModel


class _DummyFilter(BaseModel):
    type: Optional[str] = None


@pytest.fixture(autouse=True)
def _reset_registry():
    """The registry is module-level global state; reset around each test."""
    clear_query_param_schemas()
    yield
    clear_query_param_schemas()


def test_register_injects_filter_schema():
    """A filter referenced via ``generate_openapi_extra_params`` should land in
    ``components.schemas`` after ``register_query_param_schemas`` runs.
    """
    generate_openapi_extra_params(filter_schema=_DummyFilter)

    spec = {"components": {"schemas": {}}}
    spec = register_query_param_schemas(spec)

    assert "_DummyFilter" in spec["components"]["schemas"]
    assert spec["components"]["schemas"]["_DummyFilter"]["properties"]["type"]


def test_register_preserves_existing_schemas():
    generate_openapi_extra_params(filter_schema=_DummyFilter)

    spec = {"components": {"schemas": {"Existing": {"type": "object"}}}}
    spec = register_query_param_schemas(spec)

    assert "Existing" in spec["components"]["schemas"]
    assert "_DummyFilter" in spec["components"]["schemas"]


def test_clear_resets_registry_between_services():
    generate_openapi_extra_params(filter_schema=_DummyFilter)
    clear_query_param_schemas()

    spec = register_query_param_schemas({"components": {"schemas": {}}})
    assert "_DummyFilter" not in spec["components"]["schemas"]


def test_custom_openapi_hook_resolves_filter_ref():
    """End-to-end: a FastAPI app that wires ``register_query_param_schemas``
    into its ``custom_openapi`` hook emits a spec where the filter $ref
    resolves — which is exactly the regression the runtime was missing.
    """
    app = FastAPI()

    @app.get(
        "/items",
        openapi_extra=generate_openapi_extra_params(filter_schema=_DummyFilter),
    )
    async def list_items(request: Request, page: int = Query(default=1)):
        return {"data": []}

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        spec = get_openapi(title="t", version="0", routes=app.routes)
        spec = register_query_param_schemas(spec)
        app.openapi_schema = spec
        return spec

    app.openapi = custom_openapi  # type: ignore[method-assign]

    spec = TestClient(app).get("/openapi.json").json()

    assert "_DummyFilter" in spec["components"]["schemas"]
    param = next(p for p in spec["paths"]["/items"]["get"]["parameters"] if p["name"] == "filter")
    assert param["schema"]["$ref"] == "#/components/schemas/_DummyFilter"
