# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Discover local leaderboard report files from user-supplied paths.

The discovery step stays intentionally narrow: it accepts explicit files
and directories, filters by the supported report extension set defined in
the schema module, and returns a deduplicated stable path sequence for the
rest of the leaderboard pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from nemo_agents_plugin.leaderboard.schema import is_supported_report_path


def discover_report_paths(inputs: Iterable[str | Path]) -> tuple[Path, ...]:
    """Discover local leaderboard report files from explicit paths and directories.

    Rules:
    - explicit file paths must exist and must use a supported extension
    - directory paths are searched recursively for supported report files
    - paths that do not exist raise an error
    - returned paths are deduplicated and sorted for stable downstream behavior
    """

    discovered: set[Path] = set()

    for raw_input in inputs:
        path = Path(raw_input).expanduser()

        if not path.exists():
            raise FileNotFoundError(f"Input path does not exist: {path}")

        if path.is_file():
            if not is_supported_report_path(path):
                raise ValueError(f"Unsupported report file extension for path: {path}")
            discovered.add(path.resolve())
            continue

        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and is_supported_report_path(child):
                    discovered.add(child.resolve())
            continue

        raise ValueError(f"Unsupported input path type: {path}")

    return tuple(sorted(discovered))
