# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Customizer service implementation (v2 API)."""

from typing import ClassVar, List

from nmp.common.service import RouterConfig, Service
from nmp.customizer.api.v2.jobs import endpoints as jobs


class CustomizerService(Service):
    """Customization service for NeMo Platform (v2 API)."""

    dependencies: ClassVar[List[str]] = ["entities", "auth", "jobs", "secrets", "files", "models"]

    def __init__(self):
        """Initialize the customization service."""
        super().__init__(name="customization", module_name="nmp.customizer")

    @property
    def title(self) -> str:
        return "NeMo Customizer Microservice"

    @property
    def description(self) -> str:
        return "Service for customizing (fine-tuning) language models."

    def get_routers(self) -> List[RouterConfig]:
        """Return routers for the customizer service."""
        return [
            RouterConfig(
                jobs.router,
                prefix="/v2/workspaces/{workspace}",
                tag="Customizer",
                description="Customization job endpoints",
            ),
        ]
