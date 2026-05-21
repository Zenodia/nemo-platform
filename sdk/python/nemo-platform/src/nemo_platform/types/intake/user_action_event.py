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

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["UserActionEvent"]


class UserActionEvent(BaseModel):
    """Free-form user action captured by the client application.

    Use this to track arbitrary user interactions with AI responses, such as copying code,
    clicking share buttons, making purchases, or any other measurable action.

    The action identifier must be ≤256 characters and should use snake-case or kebab-case
    for consistency (e.g., ``share_clicked``, ``code_copied``, ``purchase_made``).
    """

    action: str
    """
    Descriptive name for the action taken by the user (e.g., 'share_clicked',
    'code_copied', 'link_followed'). Use snake-case or kebab-case. This is a label,
    not a unique identifier—multiple events can have the same action name.
    """

    id: Optional[str] = None
    """Unique identifier for the event. Populated when retrieved from database."""

    created_at: Optional[datetime] = None
    """UTC timestamp when the record was created."""

    created_by: Optional[Dict[str, str]] = None
    """Identifier of the user or system that generated the record.

    Can be set of key-value pairs.
    """

    event_type: Optional[Literal["user_action"]] = None

    metadata: Optional[Dict[str, Union[str, List[str], bool, float]]] = None
    """
    Optional key-value pairs with additional context about the action (max 16
    entries). Use this for details like user IDs, item IDs, timestamps, A/B test
    variants, or any other information useful for downstream training or evaluation
    pipelines. Example: {'user_id': '12345', 'experiment': 'variant_b',
    'item_purchased': 'product_456'}.
    """
