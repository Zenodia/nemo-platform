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

from typing import Iterable
from typing_extensions import Required, TypedDict

from .globals_param import GlobalsParam
from .step_definition_param import StepDefinitionParam

__all__ = ["PIIReplacerConfigParam"]


class PIIReplacerConfigParam(TypedDict, total=False):
    """Configuration for PII replacer.

    Defines how PII data should be detected and replaced in a dataset.
    """

    steps: Required[Iterable[StepDefinitionParam]]
    """List of transformation steps to perform on input data."""

    globals: GlobalsParam
    """
    Global settings for the PII replacer including locales, seed, NER, and
    classification.
    """
