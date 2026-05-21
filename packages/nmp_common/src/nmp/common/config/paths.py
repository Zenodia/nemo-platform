# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""User-data path resolution for NeMo Platform local state.

Local-development state (SQLite DB, encryption keys, file uploads) is
persisted under a user-data directory chosen via XDG-style resolution so
that values survive ``/tmp/`` cleanup on macOS reboots.
"""

from __future__ import annotations

import os
from pathlib import Path

NMP_DATA_DIR_ENV_VAR = "NMP_DATA_DIR"
XDG_DATA_HOME_ENV_VAR = "XDG_DATA_HOME"

_DATA_DIR_NAME = "nemo"
_FALLBACK_DATA_DIR = Path(f"~/.local/share/{_DATA_DIR_NAME}")


def nmp_user_data_dir() -> Path:
    """Return the directory for persistent NeMo Platform local-development state.

    Resolution order:
    1. ``$NMP_DATA_DIR`` if set
    2. ``$XDG_DATA_HOME/nemo`` if set
    3. ``~/.local/share/nemo``

    The directory is not created on call — callers should mkdir when they
    actually need to write, so read-only consumers don't materialize empty
    state directories.
    """
    override = os.environ.get(NMP_DATA_DIR_ENV_VAR)
    if override:
        return Path(override).expanduser()
    xdg = os.environ.get(XDG_DATA_HOME_ENV_VAR)
    if xdg:
        return Path(xdg).expanduser() / _DATA_DIR_NAME
    return _FALLBACK_DATA_DIR.expanduser()
