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

from typing_extensions import TypedDict

from ..._types import SequenceNotStr
from .ner_config_param import NERConfigParam
from .classify_config_param import ClassifyConfigParam

__all__ = ["GlobalsParam"]


class GlobalsParam(TypedDict, total=False):
    """
    Global settings for the PII replacer including locales, seed, NER, and classification.
    """

    classify: ClassifyConfigParam
    """Configuration for column classification using an LLM."""

    locales: SequenceNotStr[str]
    """List of locales."""

    lock_columns: SequenceNotStr[str]
    """List of columns to preserve as immutable across all transformations."""

    ner: NERConfigParam
    """Configuration for Named Entity Recognition."""

    seed: int
    """Optional random seed."""
