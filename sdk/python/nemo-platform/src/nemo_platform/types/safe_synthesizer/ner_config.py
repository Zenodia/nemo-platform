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

from typing import List, Optional

from ..._models import BaseModel
from .gliner_config import GlinerConfig

__all__ = ["NERConfig"]


class NERConfig(BaseModel):
    """Configuration for Named Entity Recognition."""

    enable_regexps: Optional[bool] = None
    """Enable NER regular expressions (experimental)."""

    gliner: Optional[GlinerConfig] = None
    """Configuration for the GLiNER named-entity recognition model."""

    ner_entities: Optional[List[str]] = None
    """List of entity types to recognize.

    If unset, classification entity types are used.
    """

    ner_threshold: Optional[float] = None
    """NER model threshold."""
