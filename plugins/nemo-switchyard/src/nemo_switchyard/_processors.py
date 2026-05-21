# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Custom Switchyard request processors used by this middleware."""

from __future__ import annotations

import logging
from typing import Any

from nemo_switchyard._format import FORMAT_TO_PATH
from switchyard.lib.proxy_context import CTX_TARGET_FORMAT
from switchyard.lib.roles import RequestProcessor

logger = logging.getLogger(__name__)

# Key used to store path updates on the Switchyard ProxyContext metadata
# so process_request can apply them to InferenceRequest.path after the pipeline runs.
CTX_PATH_UPDATE = "nemo_switchyard_path_update"


class PathUpdateProcessor(RequestProcessor):
    """Maps target format to a path update on context metadata.

    Translate sets CTX_TARGET_FORMAT during processing, indicating the format the
    request was converted to. This processor reads that and writes the corresponding
    API path to sy_context.metadata[CTX_PATH_UPDATE], where SwitchyardMiddleware
    picks it up after the pipeline runs and applies it to the InferenceRequest.

    Storing on the SY context (not IGW) is mandated by the processor interface —
    processors only see the SY ProxyContext.
    """

    async def process(self, context: Any, request: Any) -> Any:
        target_format = context.metadata.get(CTX_TARGET_FORMAT)
        if target_format:
            # CTX_TARGET_FORMAT is a ChatRequestType enum; FORMAT_TO_PATH is keyed by
            # the enum's string value (matches what users configure in `target_format`).
            key = target_format.value if hasattr(target_format, "value") else target_format
            path = FORMAT_TO_PATH.get(key)
            if path:
                context.metadata[CTX_PATH_UPDATE] = path
                logger.debug("Path update: format %r → %r", target_format, path)
        return request
