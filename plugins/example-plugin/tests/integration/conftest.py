# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Pytest fixture re-export for the example plugin integration tests.

Re-exporting :func:`igw_plugin_harness` from a project-level ``conftest.py``
is the standard pytest pattern for sharing a fixture across a test package
without importing it at the top of every test module. Listing it in
``__all__`` makes the re-export explicit so it isn't flagged as an unused
import.
"""

from nmp.core.inference_gateway.testing.fixtures import igw_plugin_harness

__all__ = ["igw_plugin_harness"]
