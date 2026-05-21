# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Configuration models for usage cases.

Note: IntakeSinkConfig has moved to switchyard.lib.factories.intake_sink
for consistency with other factory configurations. It is still re-exported
from switchyard.lib.factories.intake_sink for backwards compatibility.
"""

from switchyard.lib.config.latency_service_backend_config import (
    LatencyServiceBackendConfig,
    LatencyServiceEndpoint,
)

__all__ = [
    "LatencyServiceBackendConfig",
    "LatencyServiceEndpoint",
]
