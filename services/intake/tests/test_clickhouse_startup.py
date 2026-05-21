# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for Intake startup when ClickHouse is unavailable."""

import logging
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from nmp.intake.config import ClickHouseConfig, IntakeConfig
from nmp.intake.service import IntakeService
from nmp.testing import create_test_client


def test_intake_starts_without_clickhouse_and_trace_routes_return_503(
    caplog: pytest.LogCaptureFixture,
) -> None:
    intake_config = IntakeConfig(
        clickhouse_config=ClickHouseConfig(
            url="http://127.0.0.1:1",
            user="default",
            password="",
            database="intake_unavailable",
        )
    )
    caplog.set_level(logging.WARNING, logger="nmp.intake.service")

    with create_test_client(
        IntakeService,
        client_type=TestClient,
        service_configs={IntakeService: intake_config},
    ) as client:
        app = cast(FastAPI, client.app)
        service = cast(IntakeService, app.state.intake_service)

        assert service.clickhouse_client is not None
        assert client.get("/openapi.json").status_code == 200
        assert any(
            "ClickHouse schema setup was not run during Intake startup" in record.message for record in caplog.records
        )

        response = client.get("/apis/intake/v2/workspaces/default/spans")

    assert response.status_code == 503
    assert response.json()["detail"] == "ClickHouse spans storage unavailable"
