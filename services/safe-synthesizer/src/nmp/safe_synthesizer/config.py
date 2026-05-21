# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Configuration for the Safe Synthesizer service."""

from nmp.common.config import create_service_config_class, get_service_config


class SafeSynthesizerSettings(create_service_config_class("safe_synthesizer")):  # type: ignore
    """
    Configuration for the Safe Synthesizer service.

    Environment variables use the NMP_SAFE_SYNTHESIZER_ prefix.
    """

    host: str = "0.0.0.0"
    port: int = 8000

    entrypoint: list[str] = ["python", "-m", "nmp.safe_synthesizer.tasks.safe_synthesizer"]

    # Job executor profile for running safe-synthesizer jobs
    # Set to "e2e" for e2e tests, "default" for real execution
    job_executor_profile: str = "default"

    # TODO(v2): This should not configurable from NSS, but instead get configured on the job service
    default_job_resource_memory_request: str = "16G"
    default_job_resource_cpu_request: str = "4"
    default_job_resource_memory_limit: str = "16G"
    default_job_resource_cpu_limit: str = "4"


# Module-level singleton
config = get_service_config(SafeSynthesizerSettings)
