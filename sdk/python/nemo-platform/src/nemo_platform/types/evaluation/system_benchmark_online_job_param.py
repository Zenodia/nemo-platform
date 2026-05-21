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

from typing import Dict, Union
from typing_extensions import Required, TypeAlias, TypedDict

from .model_ref import ModelRef
from .model_param import ModelParam
from .benchmark_ref import BenchmarkRef
from .run_config_online_model_param import RunConfigOnlineModelParam

__all__ = ["SystemBenchmarkOnlineJobParam", "Model"]

Model: TypeAlias = Union[ModelParam, ModelRef]


class SystemBenchmarkOnlineJobParam(TypedDict, total=False):
    """Input for an online system benchmark evaluation job.

    Evaluates the benchmark's standard dataset against all pre-defined metrics in the benchmark.
    """

    benchmark: Required[BenchmarkRef]
    """Reference to a benchmark in the Benchmarks API.

    A reference is a string with format 'workspace/benchmark-name' that points to a
    persisted benchmark entity. See
    [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    model: Required[Model]
    """The model to evaluate."""

    benchmark_params: Dict[str, object]
    """Additional parameters specific to the benchmark."""

    params: RunConfigOnlineModelParam
    """Job parameters for model online evaluation."""
