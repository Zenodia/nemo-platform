# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Centralized temporary exclusions for automatic root test discovery."""

from pathlib import Path

TEST_DISCOVERY_EXCLUSIONS: dict[Path, str] = {
    Path("plugins/nemo-agents/tests"): "Not installed by the normal root uv environment yet.",
}
