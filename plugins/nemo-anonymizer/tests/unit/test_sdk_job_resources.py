# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import io
import tarfile
from pathlib import Path

import pandas as pd
import pytest
from nemo_anonymizer_plugin.sdk.errors import AnonymizerJobError
from nemo_anonymizer_plugin.sdk.job_resources import _safe_extract_tar
from nemo_anonymizer_plugin.sdk.job_results import AnonymizerJobResults


def _tar_with_file(name: str, content: bytes = b"data") -> io.BytesIO:
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as tar:
        info = tarfile.TarInfo(name)
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))
    stream.seek(0)
    return stream


def _tar_with_symlink(name: str, target: str) -> io.BytesIO:
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as tar:
        info = tarfile.TarInfo(name)
        info.type = tarfile.SYMTYPE
        info.linkname = target
        tar.addfile(info)
    stream.seek(0)
    return stream


def test_safe_extract_tar_rejects_parent_directory_member(tmp_path: Path) -> None:
    output_path = tmp_path / "out"
    stream = _tar_with_file("../escape.txt")

    with tarfile.open(fileobj=stream, mode="r:*") as tar:
        with pytest.raises(AnonymizerJobError, match="unsafe tar member"):
            _safe_extract_tar(tar, output_path)

    assert not (tmp_path / "escape.txt").exists()


def test_safe_extract_tar_rejects_links(tmp_path: Path) -> None:
    stream = _tar_with_symlink("artifacts/link", "/etc/passwd")

    with tarfile.open(fileobj=stream, mode="r:*") as tar:
        with pytest.raises(AnonymizerJobError, match="tar link member"):
            _safe_extract_tar(tar, tmp_path / "out")


def test_safe_extract_tar_allows_regular_files(tmp_path: Path) -> None:
    output_path = tmp_path / "out"
    stream = _tar_with_file("artifacts/dataset.txt", b"ok")

    with tarfile.open(fileobj=stream, mode="r:*") as tar:
        _safe_extract_tar(tar, output_path)

    assert (output_path / "artifacts" / "dataset.txt").read_bytes() == b"ok"


def test_job_results_load_trace_restores_original_text_column_metadata(tmp_path: Path) -> None:
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    pd.DataFrame([{"body": "Alice"}]).to_parquet(artifacts_dir / "trace.parquet", index=False)
    (artifacts_dir / "metadata.json").write_text('{"original_text_column":"body"}')

    trace = AnonymizerJobResults(artifacts_dir).load_trace()

    assert trace.attrs["original_text_column"] == "body"
