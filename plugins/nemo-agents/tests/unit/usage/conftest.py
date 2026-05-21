# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shared fixtures for ``nemo agents usage`` tests."""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the directory holding hand-written ``result.json`` fixtures."""
    return FIXTURES_DIR


@pytest.fixture
def tmp_run_dir(tmp_path: Path, fixtures_dir: Path) -> Path:
    """A single ``<ts>-<task>/`` run directory containing a result.json.

    Lays out ``<tmp_path>/20260429T220000Z-workspace-basic-mcp/result.json``
    populated from the ok-with-tokens fixture.  Use the
    :func:`run_dir_with` helper to override the source fixture.
    """
    run = tmp_path / "20260429T220000Z-workspace-basic-mcp"
    run.mkdir()
    shutil.copy(fixtures_dir / "result-ok-with-tokens.json", run / "result.json")
    return run


@pytest.fixture
def tmp_natjobs_dir(tmp_path: Path, fixtures_dir: Path) -> Path:
    """A ``nat-jobs/`` parent containing four runs (one per fixture).

    Layout:

    .. code-block:: text

        <tmp_path>/nat-jobs/
            20260429T220000Z-workspace-basic-mcp/result.json   # ok-with-tokens
            20260429T230000Z-secrets-crud-cli/result.json      # ok-null-tokens
            20260429T230500Z-files-upload-mcp/result.json      # failed-agent
            20260429T231000Z-models-list-mcp/result.json       # error-build
    """
    natjobs = tmp_path / "nat-jobs"
    natjobs.mkdir()
    layout = [
        ("20260429T220000Z-workspace-basic-mcp", "result-ok-with-tokens.json"),
        ("20260429T230000Z-secrets-crud-cli", "result-ok-null-tokens.json"),
        ("20260429T230500Z-files-upload-mcp", "result-failed-agent.json"),
        ("20260429T231000Z-models-list-mcp", "result-error-build.json"),
    ]
    for run_name, fixture_name in layout:
        run = natjobs / run_name
        run.mkdir()
        shutil.copy(fixtures_dir / fixture_name, run / "result.json")
    return natjobs


class FakeFiles:
    """Minimal stand-in for ``sdk.files`` that satisfies our download contract.

    Records each call and copies the contents of *staged_dir* into *local_path*
    on download — letting tests pre-stage a directory tree and assert it gets
    delivered to the expected destination.
    """

    def __init__(self, staged_dir: Path) -> None:
        self._staged = staged_dir
        self.calls: list[dict[str, object]] = []

    def download(
        self,
        *,
        remote_path: str,
        local_path: str,
        fileset: str,
        workspace: str,
    ) -> None:
        self.calls.append(
            {
                "remote_path": remote_path,
                "local_path": local_path,
                "fileset": fileset,
                "workspace": workspace,
            }
        )
        target = Path(local_path)
        target.mkdir(parents=True, exist_ok=True)
        for child in self._staged.iterdir():
            dest = target / child.name
            if child.is_dir():
                shutil.copytree(child, dest, dirs_exist_ok=True)
            else:
                shutil.copy(child, dest)


class FakeSDK:
    """Stand-in for ``NeMoPlatform`` exposing only the ``files`` attribute."""

    def __init__(self, staged_dir: Path) -> None:
        self.files = FakeFiles(staged_dir)


@pytest.fixture
def fake_sdk_factory() -> Iterator[type[FakeSDK]]:
    """Yield :class:`FakeSDK`; tests instantiate with their own staged dir."""
    yield FakeSDK
