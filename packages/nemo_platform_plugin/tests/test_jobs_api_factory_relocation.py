# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Verify the api_factory relocation.

The job-route factory moved from ``nmp.common.jobs.api_factory`` into
``nemo_platform_plugin.jobs.api_factory``. The old import path is kept as a thin
re-export for one minor release. These tests pin down the contract:

1. Symbols are identical through both paths (no accidental fork).
2. The old path emits a :class:`DeprecationWarning` on import.
3. Private helpers used by in-tree tests are re-exported.
"""

from __future__ import annotations

import importlib
import sys
import warnings

_PUBLIC_SYMBOLS = (
    "job_route_factory",
    "PlatformJobSpec",
    "PlatformJobStep",
    "BaseJobRequest",
    "BaseJob",
    "BaseJobsListFilter",
    "BaseJobsSortField",
    "JobRouteOption",
    "handle_job_spec_mismatch",
    "CPUExecutionProviderSpec",
    "GPUExecutionProviderSpec",
    "ContainerSpec",
    "EnvironmentVariable",
    "ResourcesSpec",
)

_PRIVATE_SYMBOLS = (
    "_validate_and_resolve_job_output",
    "_validate_job_spec",
    "_resolve_job_name",
    "_compile_platform_spec",
)


def test_new_module_importable():
    """The new canonical path imports cleanly without warnings."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        module = importlib.import_module("nemo_platform_plugin.jobs.api_factory")

    assert module.__name__ == "nemo_platform_plugin.jobs.api_factory"
    assert hasattr(module, "job_route_factory")


def test_old_path_emits_deprecation_warning():
    """Importing via the deprecated path emits DeprecationWarning exactly once."""
    # Drop any cached load of the stub so the warning fires when we re-import.
    sys.modules.pop("nmp.common.jobs.api_factory", None)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.import_module("nmp.common.jobs.api_factory")

    relevant = [
        w
        for w in caught
        if issubclass(w.category, DeprecationWarning) and "nmp.common.jobs.api_factory" in str(w.message)
    ]
    assert relevant, (
        f"Expected a DeprecationWarning mentioning nmp.common.jobs.api_factory, saw: {[str(w.message) for w in caught]}"
    )


def test_public_symbols_identical_through_both_paths():
    """Every public symbol is the same object through both paths."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        old = importlib.import_module("nmp.common.jobs.api_factory")
        new = importlib.import_module("nemo_platform_plugin.jobs.api_factory")

    for name in _PUBLIC_SYMBOLS:
        assert hasattr(old, name), f"{name} missing from old path"
        assert hasattr(new, name), f"{name} missing from new path"
        assert getattr(old, name) is getattr(new, name), (
            f"{name} diverges between nmp.common.jobs.api_factory "
            f"and nemo_platform_plugin.jobs.api_factory — the re-export is broken"
        )


def test_private_helpers_re_exported():
    """Private helpers used by in-tree tests are explicitly re-exported."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        old = importlib.import_module("nmp.common.jobs.api_factory")
        new = importlib.import_module("nemo_platform_plugin.jobs.api_factory")

    for name in _PRIVATE_SYMBOLS:
        assert hasattr(old, name), (
            f"{name} is imported by at least one in-tree test; "
            f"the nmp.common.jobs.api_factory re-export must keep it available"
        )
        assert getattr(old, name) is getattr(new, name)


def test_real_code_lives_in_nemo_platform_plugin():
    """The function's __module__ points at the new location, proving the old
    module no longer carries the implementation."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from nmp.common.jobs.api_factory import job_route_factory

    assert job_route_factory.__module__ == "nemo_platform_plugin.jobs.api_factory"
