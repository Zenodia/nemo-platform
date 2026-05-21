# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Backward-compat re-export shim.

The canonical implementation lives in ``nemo_platform_plugin.api.parsed_filter``.
Existing imports from ``nmp.common.api.parsed_filter`` continue to resolve here.
"""

from nemo_platform_plugin.api.parsed_filter import ParsedFilter as ParsedFilter
from nemo_platform_plugin.api.parsed_filter import _get_valid_fields as _get_valid_fields  # noqa: F401
from nemo_platform_plugin.api.parsed_filter import _operation_references_any as _operation_references_any  # noqa: F401
from nemo_platform_plugin.api.parsed_filter import _reverse_translate_dict as _reverse_translate_dict  # noqa: F401
from nemo_platform_plugin.api.parsed_filter import _validate_fields as _validate_fields  # noqa: F401
from nemo_platform_plugin.api.parsed_filter import make_filter_dep as make_filter_dep
