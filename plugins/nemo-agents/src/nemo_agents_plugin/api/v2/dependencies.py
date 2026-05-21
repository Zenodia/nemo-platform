# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""FastAPI dependency injection for the Agents plugin API.

Re-exports the standard NeMo Platform dependencies so route handlers can import from
a single location.
"""

from nemo_platform_plugin.entity_client import get_entity_client

__all__ = ["get_entity_client"]
