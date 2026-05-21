# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._compat import PYDANTIC_V1, ConfigDict
from ..._models import BaseModel
from .nim_deployment import NIMDeployment

__all__ = ["ModelDeploymentConfig"]


class ModelDeploymentConfig(BaseModel):
    """
    ModelDeploymentConfig stores the configuration details for deploying a model.
    These objects are immutable with automatic versioning.

    The unique identifier is the combination of workspace/name/entity_version.
    """

    created_at: datetime
    """The timestamp of model entity creation"""

    entity_version: int
    """Version of this deployment config. Automatically managed."""

    name: str
    """Name of the entity.

    Name/workspace combo must be unique across all entities. Allowed characters:
    letters (a-z, A-Z), digits (0-9), underscores, hyphens, and dots.
    """

    nim_deployment: NIMDeployment
    """Configuration for NIM-based model deployment."""

    updated_at: datetime
    """The timestamp of the last model entity update"""

    workspace: str
    """The workspace of the entity.

    Allowed characters: letters (a-z, A-Z), digits (0-9), underscores, hyphens, and
    dots.
    """

    id: Optional[str] = None
    """Unique identifier for the deployment config"""

    description: Optional[str] = None
    """Optional description of the deployment configuration"""

    model_entity_id: Optional[str] = None
    """Optional reference to the base model entity ID for this deployment"""

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    if not PYDANTIC_V1:
        # allow fields with a `model_` prefix
        model_config = ConfigDict(protected_namespaces=tuple())
