# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Safe Synthesizer service implementation."""

from typing import ClassVar, List

from fastapi import FastAPI, Request
from nmp.common.service import RouterConfig, Service
from nmp.safe_synthesizer.api.v2.jobs import endpoints as jobs
from pydantic import ValidationError
from starlette import status
from starlette.responses import JSONResponse


class SafeSynthesizerService(Service):
    """Safe Synthesizer service for NeMo Platform."""

    dependencies: ClassVar[List[str]] = ["entities", "auth", "jobs", "secrets", "files"]

    def __init__(self):
        """Initialize the safe synthesizer service."""
        super().__init__(name="safe-synthesizer", module_name="nmp.safe_synthesizer")

    @property
    def title(self) -> str:
        return "NeMo Safe Synthesizer Microservice"

    @property
    def description(self) -> str:
        return "Service for generating synthetic data and redacting PII."

    def get_routers(self) -> List[RouterConfig]:
        """Return routers for the safe synthesizer service."""
        return [
            RouterConfig(
                jobs.router,
                prefix="/v2/workspaces/{workspace}",
                tag="Safe Synthesizer",
                description="Job endpoints",
            ),
        ]

    def configure_app(self, app: FastAPI) -> None:
        """Configure the FastAPI application with exception handlers."""

        @app.exception_handler(ValidationError)
        async def validation_error_exception_handler(request: Request, ex: ValidationError):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                content={"detail": str(ex)},
            )
