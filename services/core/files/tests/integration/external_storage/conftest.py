# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Configuration for external storage integration tests.

Tests in this directory connect to external services (HuggingFace Hub, NGC, etc.)
and require network access. They are skipped by default.

To run these tests, set the RUN_EXTERNAL_STORAGE_TESTS environment variable:

    RUN_EXTERNAL_STORAGE_TESTS=1 pytest services/core/files/tests/integration/external_storage/
"""

import os
from pathlib import Path

import pytest

_THIS_DIR = Path(__file__).parent


def pytest_collection_modifyitems(config, items):
    """Add skip marker to tests in this directory if RUN_EXTERNAL_STORAGE_TESTS is not set."""
    if os.environ.get("RUN_EXTERNAL_STORAGE_TESTS"):
        return

    skip_marker = pytest.mark.skip(
        reason="External storage tests are skipped by default. Set RUN_EXTERNAL_STORAGE_TESTS=1 to run."
    )
    for item in items:
        # Only skip tests that are in this directory
        if Path(item.fspath).parent == _THIS_DIR:
            item.add_marker(skip_marker)
