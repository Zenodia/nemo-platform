# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Platform version and revision helpers."""

from __future__ import annotations

import os
from importlib.metadata import PackageNotFoundError, version

CODE_REVISION_ENV = "NMP_CODE_REVISION"
PLATFORM_VERSION_ENV = "NMP_PLATFORM_VERSION"
PACKAGE_NAMES = ("nmp-platform-runner", "nmp-platform", "nemoplatform")


def _resolve_version() -> str:
    for package_name in PACKAGE_NAMES:
        try:
            return version(package_name).strip()
        except PackageNotFoundError:
            continue
        except Exception:
            break
    return os.environ.get(PLATFORM_VERSION_ENV, "dev").strip() or "dev"


__version__ = _resolve_version()


def get_platform_version() -> str:
    return __version__


def get_revision() -> str:
    return os.environ.get(CODE_REVISION_ENV, "dev").strip() or "dev"
