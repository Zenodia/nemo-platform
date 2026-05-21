# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
"""Evaluator service implementation."""

import logging
from typing import Any, Callable, ClassVar, List

from fastapi import FastAPI, Request, Response, status
from fastapi.openapi.utils import get_openapi
from nmp.common.api.utils import IDConvertor, register_query_param_schemas, tweak_spec
from nmp.common.entities import EntityConflictError
from nmp.common.service import RouterConfig, Service
from nmp.evaluator.api.v2.benchmarks import endpoints as benchmarks
from nmp.evaluator.api.v2.metrics import endpoints as metrics
from opentelemetry import trace
from pydantic_core import ValidationError
from starlette.convertors import register_url_convertor
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "Evaluator", "description": "Operations related to evaluation."},
    {
        "name": "Health Checks",
        "description": "Operations related to NeMo Platform health.",
    },
    {"name": "Internal API", "description": "Internal endpoints for job status updates."},
]


class CaptureTraceId(BaseHTTPMiddleware):
    """Middleware to capture and return trace ID in response headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        trace_id = trace.get_current_span().get_span_context().trace_id
        response = await call_next(request)
        response.headers["X-Trace-Id"] = format(trace_id, "x")
        return response


class EvaluatorService(Service):
    """Evaluation service for NeMo Platform."""

    dependencies: ClassVar[List[str]] = ["entities", "auth", "secrets", "jobs", "files"]

    def __init__(self):
        """Initialize the evaluation service."""
        super().__init__(name="evaluation", module_name="nmp.evaluator")

    @property
    def title(self) -> str:
        return "NeMo Evaluator Microservice"

    @property
    def description(self) -> str:
        return "The NeMo Evaluator is the one-stop shop for evaluation needs as part of the NeMo Platform ecosystem."

    def get_routers(self) -> List[RouterConfig]:
        """Return routers for the evaluator service."""
        return [
            RouterConfig(
                benchmarks.router,
                tag="Evaluator",
                description="Evaluation benchmark endpoints",
            ),
            RouterConfig(
                metrics.router,
                tag="Evaluator",
                description="Evaluation metric endpoints",
            ),
        ]

    async def on_startup(self) -> None:
        """Initialize service on startup."""
        # Register URL convertor
        register_url_convertor("id", IDConvertor())

    def create_app(self) -> FastAPI:
        """Create and return the FastAPI application with custom middleware and handlers."""
        # Call parent to create base app
        app = super().create_app()

        # Add trace ID middleware
        app.add_middleware(CaptureTraceId)  # ty: ignore[invalid-argument-type]

        # Register exception handlers
        self._register_exception_handlers(app)

        # Custom OpenAPI schema
        def custom_openapi() -> dict[str, Any]:
            return self._custom_openapi(app)

        setattr(app, "openapi", custom_openapi)

        return app

    def _register_exception_handlers(self, app: FastAPI) -> None:
        """Register custom exception handlers."""

        @app.exception_handler(ValidationError)
        async def validation_error_handler(request: Request, ex: ValidationError):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                content={"detail": str(ex)},
            )

        @app.exception_handler(EntityConflictError)
        async def resource_already_exists_handler(request: Request, ex: EntityConflictError):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": str(ex)},
            )

        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )

    def _custom_openapi(self, app: FastAPI) -> dict[str, Any]:
        """Generate custom OpenAPI schema."""
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=self.title,
            version=self.version,
            summary=self.description,
            description="",
            routes=app.routes,
            tags=tags_metadata,
        )
        openapi_schema = register_query_param_schemas(openapi_schema)
        openapi_schema = tweak_spec(openapi_schema)
        app.openapi_schema = openapi_schema
        return app.openapi_schema
