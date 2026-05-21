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

from typing import Dict
from typing_extensions import Required, TypedDict

from .fileset_ref import FilesetRef
from .benchmark_ref import BenchmarkRef
from .run_config_param import RunConfigParam

__all__ = ["SystemBenchmarkOfflineJobParam"]


class SystemBenchmarkOfflineJobParam(TypedDict, total=False):
    """Input for an offline system benchmark evaluation job.

    Evaluates the benchmark's standard dataset against all pre-defined metrics in the benchmark.
    """

    benchmark: Required[BenchmarkRef]
    """Reference to a benchmark in the Benchmarks API.

    A reference is a string with format 'workspace/benchmark-name' that points to a
    persisted benchmark entity. See
    [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    dataset: Required[FilesetRef]
    """Reference to a Fileset in the Files API.

    A reference is a string with format 'workspace/fileset-name' that points to a
    persisted fileset entity. When used as a dataset source, all files within the
    fileset will be downloaded to the job container.

    See [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    benchmark_params: Dict[str, object]
    """Additional parameters specific to the benchmark."""

    params: RunConfigParam
    """Job parameters."""
