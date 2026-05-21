# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import sys
from pathlib import Path

AGENTIC_USE_DIR = Path(__file__).resolve().parents[1]

# nat_runner and seed_providers live in tests/agentic-use/ (not a package).
sys.path.insert(0, str(AGENTIC_USE_DIR))
sys.path.insert(0, str(AGENTIC_USE_DIR / "shared"))
