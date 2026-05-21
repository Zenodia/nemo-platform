# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Minimal Sphinx configuration for integration testing."""

project = "NeMo-NB Integration Test"
extensions = [
    "myst_parser",
    "sphinx_design",
    "nemo_nb",
]

# MyST parser config
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# NeMo-NB config
nemo_nb_config = {}

# Basic Sphinx config
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "alabaster"
