# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from nmp.common.observability.metrics import _format_metric_name


def test_format_metric_name():
    assert _format_metric_name("nmp", "secrets", "api_requests_total") == "nmp.secrets.api.requests.total"
    assert _format_metric_name("nmp", "", "api_requests_total") == "nmp.api.requests.total"
    assert _format_metric_name("nmp", "backend_service", "error_count") == "nmp.backend.service.error.count"
    assert (
        _format_metric_name("customnamespace", "customsubsystem", "custom_metric_name")
        == "customnamespace.customsubsystem.custom.metric.name"
    )
