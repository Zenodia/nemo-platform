# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Discover Harbor evals by scanning tests/agentic-use/ for task.toml files."""

import tomllib
from fnmatch import fnmatch
from pathlib import Path

from nemo_agents_plugin.improvement.models import Difficulty, EvalSpec

# Directories within tests/agentic-use/ that are NOT evals
EXCLUDED_DIRS = frozenset(
    {
        "shared",
        "scripts",
        "reports",
        "agentic_flows",
        "example-test-template",
    }
)

# Required files for a valid eval
REQUIRED_FILES = [
    "task.toml",
    "instruction.md",
    "tests/test_outputs.py",
]


def _parse_difficulty(raw: str) -> Difficulty:
    """Parse difficulty string from task.toml, defaulting to MEDIUM."""
    raw = raw.strip().lower()
    try:
        return Difficulty(raw)
    except ValueError:
        return Difficulty.MEDIUM


def parse_task_toml(eval_dir: Path) -> EvalSpec:
    """Parse a single task.toml into an EvalSpec.

    Args:
        eval_dir: Path to the eval directory containing task.toml.

    Returns:
        An EvalSpec with parsed metadata.

    Raises:
        FileNotFoundError: If task.toml doesn't exist.
        KeyError: If required fields are missing.
    """
    task_toml = eval_dir / "task.toml"
    data = tomllib.loads(task_toml.read_text())

    metadata = data.get("metadata", {})
    agent = data.get("agent", {})
    verifier = data.get("verifier", {})

    return EvalSpec(
        name=eval_dir.name,
        path=eval_dir,
        difficulty=_parse_difficulty(metadata.get("difficulty", "medium")),
        category=metadata.get("category", ""),
        tags=list(metadata.get("tags", [])),
        agent_timeout_sec=float(agent.get("timeout_sec", 600.0)),
        verifier_timeout_sec=float(verifier.get("timeout_sec", 60.0)),
    )


def discover_evals(
    agentic_use_dir: Path,
    filter_glob: str | None = None,
    filter_names: set[str] | None = None,
    difficulty: Difficulty | None = None,
    category: str | None = None,
    tags: list[str] | None = None,
    easy_only: bool = False,
    standard_only: bool = False,
) -> list[EvalSpec]:
    """Scan agentic-use/ for directories with task.toml and apply filters.

    Args:
        agentic_use_dir: Path to the tests/agentic-use/ directory.
        filter_glob: Glob pattern to match eval names (e.g. "files-*").
        difficulty: Only include evals with this difficulty.
        category: Only include evals with this category.
        tags: Only include evals that have ALL of these tags.
        easy_only: Only include evals whose name ends with "-easy".
        standard_only: Exclude evals whose name ends with "-easy".

    Returns:
        List of EvalSpec objects, sorted by name.
    """
    if not agentic_use_dir.is_dir():
        return []

    # Resolve to absolute path so eval paths work from any working directory
    agentic_use_dir = agentic_use_dir.resolve()

    specs: list[EvalSpec] = []

    for child in sorted(agentic_use_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name in EXCLUDED_DIRS:
            continue
        if not (child / "task.toml").exists():
            continue

        # Validate required files exist
        missing = [f for f in REQUIRED_FILES if not (child / f).exists()]
        if missing:
            continue

        try:
            spec = parse_task_toml(child)
        except (FileNotFoundError, KeyError, ValueError, TypeError, tomllib.TOMLDecodeError):
            continue

        # Apply filters
        if filter_names and spec.name not in filter_names:
            continue
        if filter_glob and not fnmatch(spec.name, filter_glob):
            continue
        if easy_only and not spec.name.endswith("-easy"):
            continue
        if standard_only and spec.name.endswith("-easy"):
            continue
        if difficulty and spec.difficulty != difficulty:
            continue
        if category and spec.category != category:
            continue
        if tags and not all(t in spec.tags for t in tags):
            continue

        specs.append(spec)

    return specs


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from start (or cwd) to find the monorepo root (has pyproject.toml with workspace)."""
    current = start or Path.cwd()
    for parent in [current, *current.parents]:
        pyproject = parent / "pyproject.toml"
        if pyproject.exists() and (parent / "tests" / "agentic-use").is_dir():
            return parent
    raise FileNotFoundError("Could not find project root (no tests/agentic-use/ directory found)")


def get_agentic_use_dir(project_root: Path | None = None) -> Path:
    """Get the tests/agentic-use/ directory path."""
    root = project_root or find_project_root()
    return root / "tests" / "agentic-use"
