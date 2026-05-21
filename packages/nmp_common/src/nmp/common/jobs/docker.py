# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Docker-specific job validation compatibility wrapper."""

import logging

from nemo_platform.types.jobs import PlatformJobSpecParam
from nemo_platform_plugin.jobs.docker import spec_has_gpu_step as spec_has_gpu_step
from nmp.common.config import Runtime, get_platform_config
from nmp.common.jobs.exceptions import PlatformJobCompilationError
from pydantic import ValidationError

logger = logging.getLogger(__name__)

_GPU_UNAVAILABLE_MSG = (
    "This job requires a GPU. The platform is running on Docker with no GPUs "
    "configured. Configure GPUs in platform config or use a GPU-enabled environment."
)


def validate_gpu_available_for_docker(job: PlatformJobSpecParam) -> None:
    """Fail fast when job requires GPU but platform is Docker with no GPUs configured."""
    try:
        platform_config = get_platform_config()
    except (ValueError, OSError, ValidationError):
        logger.debug("Skipping GPU availability validation: could not load platform config")
        return

    if platform_config.runtime != Runtime.DOCKER:
        return

    reserved_ids = platform_config.docker.get_reserved_gpu_ids()
    if reserved_ids is None:
        return
    if len(reserved_ids) > 0:
        return

    if not spec_has_gpu_step(job):
        return

    raise PlatformJobCompilationError(_GPU_UNAVAILABLE_MSG)
