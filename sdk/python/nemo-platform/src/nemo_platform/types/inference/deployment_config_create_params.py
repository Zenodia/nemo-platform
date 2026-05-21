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

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .nim_deployment_param import NIMDeploymentParam

__all__ = ["DeploymentConfigCreateParams"]


class DeploymentConfigCreateParams(TypedDict, total=False):
    workspace: str

    name: Required[str]
    """Name of the deployment configuration.

    Allowed characters: letters (a-z, A-Z), digits (0-9), underscores, hyphens, and
    dots.
    """

    nim_deployment: Required[NIMDeploymentParam]
    """Configuration for NIM-based model deployment."""

    description: str
    """Optional description of the deployment configuration"""

    model_entity_id: str
    """Optional reference to the base model entity ID for this deployment"""

    project: str
    """The URN of the project associated with this deployment configuration"""
