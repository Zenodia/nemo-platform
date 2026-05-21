# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OSS-router factory — wraps an external routing plugin behind the chain.

See :mod:`switchyard.lib.plugin` for the plugin contract and
:mod:`switchyard.lib.processors.plugin_routing_request_processor` for the
request-side integration.
"""

from switchyard.lib.factories.oss_router.factory import (
    OSSRouterConfig,
    OSSRouterFactory,
    OSSRouterTier,
)

__all__ = [
    "OSSRouterConfig",
    "OSSRouterFactory",
    "OSSRouterTier",
]
