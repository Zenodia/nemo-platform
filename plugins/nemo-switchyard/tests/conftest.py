# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test bootstrap.

The Switchyard library used by this plugin is not yet on PyPI; until it is, dev
machines need its source on the import path. We try a real import first; if the
PyPI ``switchyard`` package is shadowing it (a different project with the same
name), evict it from sys.modules and prepend ~/repos/github/switchyard. Production
deployments should set PYTHONPATH (or install the wheel once published) rather
than relying on this fallback.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def _bootstrap_switchyard() -> None:
    try:
        importlib.import_module("switchyard.lib.proxy_context")
        return
    except ImportError:
        pass

    github_path = Path.home() / "repos" / "github" / "switchyard"
    if not github_path.exists():
        return

    # Drop any partially imported switchyard so the github copy wins on re-import.
    for mod_name in [m for m in sys.modules if m == "switchyard" or m.startswith("switchyard.")]:
        del sys.modules[mod_name]

    sys.path.insert(0, str(github_path))


_bootstrap_switchyard()
