# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test fixtures for Customizer service tests."""

import sys
from pathlib import Path

# Add parent directory to sys.path so we can import modules like `constants`
# without relative imports (which don't work in test files).
sys.path.insert(0, str(Path(__file__).parent))


import pytest


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection.

    Auto-marks tests based on their location:

    - Tests in e2e/ directories get the 'e2e' marker
    - Tests in integration/ directories get the 'integration' marker
    - Tests without category markers get the 'unit' marker
    """
    category_markers = {"unit", "e2e", "integration", "regression", "canary", "slow", "skip_in_ci"}

    for item in items:
        marker_names = {marker.name for marker in item.iter_markers()}

        if "/e2e/" in str(item.fspath):
            if "e2e" not in marker_names:
                item.add_marker(pytest.mark.e2e)
                marker_names.add("e2e")
        elif "/integration/" in str(item.fspath):
            if "integration" not in marker_names:
                item.add_marker(pytest.mark.integration)
                marker_names.add("integration")

        if not marker_names.intersection(category_markers):
            item.add_marker(pytest.mark.unit)
