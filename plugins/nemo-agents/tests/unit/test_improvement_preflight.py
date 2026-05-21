# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the improvement/preflight.py module."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from nemo_agents_plugin.improvement import preflight as preflight_mod
from nemo_agents_plugin.improvement.preflight import (
    PreflightError,
    check_anthropic_api,
    check_dockerfile,
    check_evals_dir,
    check_forge_tooling,
)


def test_check_evals_dir_skips_unreadable_children(tmp_path: Path) -> None:
    """Unreadable subdirs (e.g. systemd-private under /tmp) must not crash the scan."""
    unreadable = tmp_path / "unreadable"
    unreadable.mkdir(mode=0o000)
    try:
        with pytest.raises(PreflightError, match="No eval tasks found"):
            check_evals_dir(tmp_path)
    finally:
        unreadable.chmod(0o755)


def test_check_evals_dir_finds_task_alongside_unreadable(tmp_path: Path) -> None:
    """A valid task dir must still be discovered even when a sibling is unreadable."""
    unreadable = tmp_path / "unreadable"
    unreadable.mkdir(mode=0o000)
    valid = tmp_path / "valid-task"
    valid.mkdir()
    (valid / "task.toml").write_text("[metadata]\n")
    try:
        check_evals_dir(tmp_path)
    finally:
        unreadable.chmod(0o755)


@pytest.mark.skipif(os.geteuid() == 0, reason="root bypasses permission checks")
def test_check_evals_dir_unreadable_root_raises_clean_error(tmp_path: Path) -> None:
    """An unreadable evals_dir itself produces a PreflightError, not a stack trace."""
    unreadable_root = tmp_path / "unreadable-root"
    unreadable_root.mkdir(mode=0o000)
    try:
        with pytest.raises(PreflightError, match="Cannot read --evals directory"):
            check_evals_dir(unreadable_root)
    finally:
        unreadable_root.chmod(0o755)


def test_check_anthropic_api_raises_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    with pytest.raises(PreflightError, match="ANTHROPIC_API_KEY"):
        check_anthropic_api()


def test_check_anthropic_api_passes_with_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    check_anthropic_api()


def test_check_anthropic_api_passes_with_auth_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "tok-test")
    check_anthropic_api()


def test_check_forge_tooling_raises_when_neither_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight_mod, "_which", lambda _: None)
    with pytest.raises(PreflightError, match="open_pr=True requires"):
        check_forge_tooling()


def test_check_forge_tooling_passes_with_gh(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight_mod, "_which", lambda name: "/usr/bin/gh" if name == "gh" else None)
    check_forge_tooling()


def test_check_forge_tooling_passes_with_glab(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight_mod, "_which", lambda name: "/usr/bin/glab" if name == "glab" else None)
    check_forge_tooling()


def test_check_dockerfile_raises_when_missing(tmp_path: Path) -> None:
    with pytest.raises(PreflightError, match=r"Dockerfile\.agentic-base not found"):
        check_dockerfile(tmp_path)


def test_check_dockerfile_passes_when_present(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile.agentic-base").write_text("FROM scratch\n")
    check_dockerfile(tmp_path)
