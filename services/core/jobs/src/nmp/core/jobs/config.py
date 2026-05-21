# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Configuration for the Jobs service."""

from typing import Self

from nmp.common.config import create_service_config_class, get_platform_config, get_service_config
from nmp.core.jobs.app.profiles import ExecutionProfileT
from nmp.core.jobs.controllers.backends.config import (
    DefaultExecutionProfileConfig,
    get_default_executor_profiles_for_runtime,
    merge_executor_profiles,
)
from pydantic import Field, model_validator


class JobsServiceConfig(create_service_config_class("jobs")):  # type: ignore
    """
    Configuration for the Jobs Service.

    Environment variables use the NMP_JOBS_ prefix.
    """

    executors: list[ExecutionProfileT] = Field(
        default_factory=list, description="List of executor profiles for the Jobs service"
    )
    executor_defaults: DefaultExecutionProfileConfig = Field(
        default_factory=DefaultExecutionProfileConfig, description="Default executor profile configurations"
    )
    reconcile_interval_seconds: int = Field(default=2, description="Interval in seconds for the job reconciler to run")
    schedule_interval_seconds: int = Field(default=5, description="Interval in seconds for the job scheduler to run")

    @model_validator(mode="after")
    def validate_executors(self) -> Self:
        """
        Validates that executor profiles have unique (provider, profile) combinations.
        Raises a ValueError if duplicates are found.
        """
        seen_keys = set()
        for executor in self.executors:
            key = (executor.provider, executor.profile)
            if key in seen_keys:
                raise ValueError(
                    f"Duplicate executor profile found for provider '{executor.provider}' and profile '{executor.profile}'"
                )
            seen_keys.add(key)
        return self


# Module-level singleton instances
config = get_service_config(JobsServiceConfig)
profiles = merge_executor_profiles(
    config.executors,
    get_default_executor_profiles_for_runtime(
        runtime=get_platform_config().runtime,
        defaults=config.executor_defaults,
    ),
)
