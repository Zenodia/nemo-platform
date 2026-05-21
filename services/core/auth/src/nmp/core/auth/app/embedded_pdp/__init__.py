# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Embedded Policy Decision Point (PDP) using OPA WASM.

This package provides an embedded policy evaluation engine that runs
OPA policies compiled to WebAssembly, eliminating the need for an
external OPA sidecar.
"""

from .data import apply_embedded_policy_document, load_policy_data
from .engine import (
    OPAPolicy,
    PolicyEngineError,
    evaluate,
    get_policy,
    get_valid_entrypoints,
    reload_policy,
    set_policy_data,
    validate_entrypoint,
)

__all__ = [
    # Engine
    "OPAPolicy",
    "PolicyEngineError",
    "evaluate",
    "get_policy",
    "get_valid_entrypoints",
    "reload_policy",
    "set_policy_data",
    "validate_entrypoint",
    "load_policy_data",
    "apply_embedded_policy_document",
]
