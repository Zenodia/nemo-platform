# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests to ensure lint tool versions stay synchronized across config files."""

import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent.parent


def test_ruff_versions_match():
    """Ensure ruff version in pre-commit matches pyproject.toml dev dependency."""

    def _get_pre_commit_ruff_version() -> str | None:
        """Extract ruff version from .pre-commit-config.yaml."""
        with open(ROOT / ".pre-commit-config.yaml") as f:
            config = yaml.safe_load(f)
        for repo in config.get("repos", []):
            if "ruff-pre-commit" in repo.get("repo", ""):
                return repo.get("rev", "").lstrip("v")
        return None

    def _get_pyproject_ruff_version() -> str | None:
        """Extract ruff version from pyproject.toml dev dependencies."""
        with open(ROOT / "pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        for dep in config.get("dependency-groups", {}).get("dev", []):
            if isinstance(dep, str) and dep.startswith("ruff=="):
                return dep.split("==")[1]
        return None

    pre_commit_version = _get_pre_commit_ruff_version()
    pyproject_version = _get_pyproject_ruff_version()

    assert pre_commit_version, "Could not find ruff version in .pre-commit-config.yaml"
    assert pyproject_version, "Could not find ruff==X.Y.Z in pyproject.toml dev dependencies"
    assert pre_commit_version == pyproject_version, (
        f"Ruff version mismatch: pre-commit has {pre_commit_version}, "
        f"pyproject.toml has {pyproject_version}. "
        "Update both to the same version to avoid formatting conflicts."
    )
