# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Load leaderboard report JSON into plain Python mappings.

This layer is intentionally thin: it validates that each file contains a
top-level JSON object and normalizes keys to plain strings, but leaves
schema validation and semantic coercion to the downstream normalize step.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_report(path: str | Path) -> dict[str, object]:
    """Load a single leaderboard report from a JSON file.

    The current schema expects one JSON object per report file.
    """

    resolved_path = Path(path).expanduser()
    try:
        data = json.loads(resolved_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse JSON report file {resolved_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Report file must contain a top-level JSON object: {resolved_path}")

    return _normalize_loaded_object(data)


def load_reports(paths: tuple[Path, ...]) -> tuple[dict[str, object], ...]:
    """Load multiple leaderboard reports from JSON files in order."""
    return tuple(load_report(path) for path in paths)


def _normalize_loaded_object(data: dict[str, Any]) -> dict[str, object]:
    """Return a plain object-only dict for downstream processing."""
    return {str(key): value for key, value in data.items()}
