# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from nemo_platform import AsyncNeMoPlatform, NeMoPlatform


def async_to_sync_sdk(async_sdk: AsyncNeMoPlatform) -> NeMoPlatform:
    """Build a sync :class:`NeMoPlatform` mirroring the async SDK's config."""
    return NeMoPlatform(
        base_url=async_sdk.base_url,
        default_headers=dict(async_sdk._custom_headers) if async_sdk._custom_headers else None,
        default_query=dict(async_sdk._custom_query) if async_sdk._custom_query else None,
        timeout=async_sdk.timeout,
        max_retries=async_sdk.max_retries,
        workspace=async_sdk.workspace,
    )


def sync_to_async_sdk(sdk: NeMoPlatform) -> AsyncNeMoPlatform:
    """Build an async :class:`AsyncNeMoPlatform` mirroring the sync SDK's config."""
    return AsyncNeMoPlatform(
        base_url=sdk.base_url,
        default_headers=dict(sdk._custom_headers) if sdk._custom_headers else None,
        default_query=dict(sdk._custom_query) if sdk._custom_query else None,
        timeout=sdk.timeout,
        max_retries=sdk.max_retries,
        workspace=sdk.workspace,
    )
