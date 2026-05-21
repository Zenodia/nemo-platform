# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

import pytest
from nmp.evaluator.tasks.download_fileset.__main__ import main, move_to_target
from pytest_mock import MockerFixture


class TestMoveToTarget:
    def test_replaces_existing_file_collision(self, tmp_path: Path):
        local_dir = tmp_path / "local"
        target_dir = tmp_path / "target"
        local_dir.mkdir()
        target_dir.mkdir()

        (local_dir / "dataset.json").write_text("new")
        (target_dir / "dataset.json").write_text("old")

        move_to_target(str(local_dir), str(target_dir))

        assert (target_dir / "dataset.json").read_text() == "new"
        assert not any(local_dir.iterdir())

    def test_replaces_existing_directory_collision(self, tmp_path: Path):
        local_dir = tmp_path / "local"
        target_dir = tmp_path / "target"
        local_dir.mkdir()
        target_dir.mkdir()

        (local_dir / "dataset").mkdir()
        (local_dir / "dataset" / "new.json").write_text("new")
        (target_dir / "dataset").mkdir()
        (target_dir / "dataset" / "old.json").write_text("old")

        move_to_target(str(local_dir), str(target_dir))

        moved_dir = target_dir / "dataset"
        assert moved_dir.is_dir()
        assert (moved_dir / "new.json").read_text() == "new"
        assert not (moved_dir / "old.json").exists()


class TestMain:
    @pytest.mark.asyncio
    async def test_expands_env_vars_and_copies_when_target_dir_provided(
        self, tmp_path: Path, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
    ):
        local_root = tmp_path / "local-root"
        target_root = tmp_path / "target-root"
        monkeypatch.setenv("LOCAL_ROOT", str(local_root))
        monkeypatch.setenv("TARGET_ROOT", str(target_root))

        mock_download_dataset = mocker.patch(
            "nmp.evaluator.tasks.download_fileset.__main__.download_dataset",
            new=mocker.AsyncMock(),
        )
        mock_move_to_target = mocker.patch("nmp.evaluator.tasks.download_fileset.__main__.move_to_target")

        result = await main(
            [
                "--dataset",
                json.dumps({"rows": [{"x": 1}]}),
                "--local-dir",
                "${LOCAL_ROOT}/scratch",
                "--target-dir",
                "${TARGET_ROOT}/datasets",
            ],
            sdk=mocker.Mock(),
        )

        assert result == 0
        mock_download_dataset.assert_awaited_once()
        assert mock_download_dataset.await_args.kwargs["destination"] == str(local_root / "scratch")
        mock_move_to_target.assert_called_once_with(str(local_root / "scratch"), str(target_root / "datasets"))

    @pytest.mark.asyncio
    async def test_does_not_copy_when_target_dir_not_provided(self, mocker: MockerFixture):
        mock_download_dataset = mocker.patch(
            "nmp.evaluator.tasks.download_fileset.__main__.download_dataset",
            new=mocker.AsyncMock(),
        )
        mock_move_to_target = mocker.patch("nmp.evaluator.tasks.download_fileset.__main__.move_to_target")

        result = await main(
            [
                "--dataset",
                json.dumps({"rows": [{"x": 1}]}),
                "--local-dir",
                "/tmp/local",
            ],
            sdk=mocker.Mock(),
        )

        assert result == 0
        mock_download_dataset.assert_awaited_once()
        mock_move_to_target.assert_not_called()

    @pytest.mark.asyncio
    async def test_does_not_copy_when_local_and_target_are_equal(self, mocker: MockerFixture):
        mock_download_dataset = mocker.patch(
            "nmp.evaluator.tasks.download_fileset.__main__.download_dataset",
            new=mocker.AsyncMock(),
        )
        mock_move_to_target = mocker.patch("nmp.evaluator.tasks.download_fileset.__main__.move_to_target")

        result = await main(
            [
                "--dataset",
                json.dumps({"rows": [{"x": 1}]}),
                "--local-dir",
                "/tmp/same",
                "--target-dir",
                "/tmp/same",
            ],
            sdk=mocker.Mock(),
        )

        assert result == 0
        mock_download_dataset.assert_awaited_once()
        mock_move_to_target.assert_not_called()
