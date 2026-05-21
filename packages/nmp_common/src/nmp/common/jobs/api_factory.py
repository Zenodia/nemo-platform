# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Deprecated — re-exports from :mod:`nemo_platform_plugin.jobs.api_factory`.

The job-route factory moved out of ``nmp_common`` and into ``nemo-platform-plugin``.
This module remains as a thin re-export for one minor release so in-tree services
and plugin authors have time to update their imports.

Replace::

    from nmp.common.jobs.api_factory import job_route_factory, PlatformJobSpec, ...

with::

    from nemo_platform_plugin.jobs.api_factory import job_route_factory, PlatformJobSpec, ...

After the deprecation window, this module will be deleted.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "nmp.common.jobs.api_factory has moved to nemo_platform_plugin.jobs.api_factory. "
    "Update imports before the next minor release — the old path will be removed.",
    DeprecationWarning,
    stacklevel=2,
)

from nemo_platform_plugin.jobs.api_factory import *  # noqa: E402, F401, F403

# Private helpers used by a few in-tree tests. Wildcard import above
# excludes underscore-prefixed names, so re-export explicitly.
from nemo_platform_plugin.jobs.api_factory import (  # noqa: E402, F401
    _accepts_entity_client,
    _compile_platform_spec,
    _is_basemodel_union,
    _is_union_type,
    _resolve_job_name,
    _transform_input_to_output,
    _unwrap_annotated_schema,
    _validate_and_resolve_job_output,
    _validate_basemodel_or_union,
    _validate_job_spec,
)
