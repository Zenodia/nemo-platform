# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""RunnerBackendRegistry — factory that instantiates the configured backend."""

from __future__ import annotations

import logging

from nemo_agents_plugin.config import AgentsConfig
from nemo_agents_plugin.runner.backend import RunnerBackend

logger = logging.getLogger(__name__)


class RunnerBackendRegistry:
    """Instantiates and holds the active :class:`~nemo_agents_plugin.runner.backend.RunnerBackend`.

    The backend type is determined by :attr:`~nemo_agents_plugin.config.AgentsConfig.runner_backend`.
    Currently only ``"in_memory"`` is supported.

    Future backends register here:
    - ``"docker"``  → ``DockerRunnerBackend``
    - ``"k8s"``     → ``K8sRunnerBackend``
    """

    def __init__(self, config: AgentsConfig) -> None:
        backend_type = config.runner_backend
        if backend_type == "in_memory":
            from nemo_agents_plugin.runner.in_memory import InMemoryRunnerBackend

            self._backend: RunnerBackend = InMemoryRunnerBackend(config.controller)
            logger.info(
                "Runner backend: InMemoryRunnerBackend (port range start=%d)", config.controller.port_range_start
            )
        else:
            raise ValueError(f"Unknown runner_backend type '{backend_type}'. Supported values: 'in_memory'.")

    @property
    def backend(self) -> RunnerBackend:
        """The active backend instance."""
        return self._backend
