# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Request
from nemo_platform_plugin.service import NemoService, RouterSpec
from nmp.platform_runner.plugin_adapter import NemoServiceAdapter
from starlette.responses import JSONResponse


class _StubService(NemoService):
    name = "test-plugin"

    def get_routers(self) -> list[RouterSpec]:
        return [RouterSpec(router=APIRouter())]


class _ServiceWithExceptionHandlers(NemoService):
    name = "test-plugin"

    def get_routers(self) -> list[RouterSpec]:
        return [RouterSpec(router=APIRouter())]

    def get_exception_handlers(self):
        async def handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
            return JSONResponse(status_code=422, content={"detail": str(exc)})

        return {ValueError: handle_value_error}


def test_adapter_without_exception_handlers():
    adapter = NemoServiceAdapter(_StubService())
    app = adapter.create_app()
    assert ValueError not in app.exception_handlers


def test_adapter_registers_exception_handlers():
    adapter = NemoServiceAdapter(_ServiceWithExceptionHandlers())
    app = adapter.create_app()
    assert ValueError in app.exception_handlers
