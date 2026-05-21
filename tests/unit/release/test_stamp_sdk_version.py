# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def load_stamp_module() -> ModuleType:
    script_path = Path(__file__).parents[3] / ".github/scripts/stamp_sdk_version.py"
    spec = importlib.util.spec_from_file_location("stamp_sdk_version", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


stamp_sdk_version = load_stamp_module()
StampError = stamp_sdk_version.StampError


def write_source_tree(
    source_root: Path,
    *,
    shared_assignment: str = 'platform_sdk_version = "2.1.0"',
    sdk_assignment: str = '__version__ = "2.1.0"',
) -> None:
    shared_version_dir = source_root / "packages/nmp_common/src/nmp/common"
    sdk_dir = source_root / "sdk/python/nemo-platform"
    sdk_version_dir = sdk_dir / "src/nemo_platform"

    shared_version_dir.mkdir(parents=True)
    sdk_version_dir.mkdir(parents=True)
    (sdk_dir / "pyproject.toml").write_text('[project]\nname = "nemo-platform-sdk"\n', encoding="utf-8")
    (shared_version_dir / "version.py").write_text(f"{shared_assignment}\n", encoding="utf-8")
    (sdk_version_dir / "_version.py").write_text(f"{sdk_assignment}\n", encoding="utf-8")


def read_versions(source_root: Path) -> tuple[str, str]:
    shared_version = (source_root / "packages/nmp_common/src/nmp/common/version.py").read_text(encoding="utf-8")
    sdk_version = (source_root / "sdk/python/nemo-platform/src/nemo_platform/_version.py").read_text(encoding="utf-8")
    return shared_version, sdk_version


def stamp(
    source_root: Path,
    *,
    sdk_id: str = "nemo-platform",
    cadence: str = "release",
    release_label: str = "1.0.0",
    nightly_timestamp: str = "",
) -> str:
    return stamp_sdk_version.stamp_sdk_version(
        source_root=source_root,
        sdk_id=sdk_id,
        cadence=cadence,
        release_label=release_label,
        nightly_timestamp=nightly_timestamp,
    )


def test_nightly_stamps_dev_version(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(source_root)

    version = stamp(
        source_root,
        cadence="nightly",
        release_label="nightly-20260512010101",
        nightly_timestamp="20260512010101",
    )

    assert version == "2.1.0.dev20260512010101"
    assert read_versions(source_root) == (
        'platform_sdk_version = "2.1.0.dev20260512010101"\n',
        '__version__ = "2.1.0.dev20260512010101"\n',
    )


def test_rc_stamps_python_rc_version(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(source_root)

    version = stamp(source_root, cadence="rc", release_label="1.2.3-rc12")

    assert version == "1.2.3rc12"
    assert read_versions(source_root) == (
        'platform_sdk_version = "1.2.3rc12"\n',
        '__version__ = "1.2.3rc12"\n',
    )


def test_stable_stamps_release_label(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(source_root)

    version = stamp(source_root, cadence="release", release_label="1.0.0")

    assert version == "1.0.0"
    assert read_versions(source_root) == ('platform_sdk_version = "1.0.0"\n', '__version__ = "1.0.0"\n')


@pytest.mark.parametrize("sdk_id", ["../nemo-platform", ".", "..", "bad/id", "bad id"])
def test_unsafe_sdk_id_fails(tmp_path: Path, sdk_id: str):
    source_root = tmp_path / "source"
    write_source_tree(source_root)

    with pytest.raises(StampError, match="safe single path segment"):
        stamp(source_root, sdk_id=sdk_id)


def test_nemo_platform_plugin_stamps_checkout_without_sdk_python_package(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(source_root)

    version = stamp(source_root, sdk_id="nemo-platform-plugin", cadence="release", release_label="1.0.0")

    assert version == "1.0.0"
    assert read_versions(source_root) == ('platform_sdk_version = "1.0.0"\n', '__version__ = "1.0.0"\n')


def test_missing_shared_version_file_fails(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(source_root)
    (source_root / "packages/nmp_common/src/nmp/common/version.py").unlink()

    with pytest.raises(StampError, match="version file is missing"):
        stamp(source_root)


@pytest.mark.parametrize(
    "base_version",
    ["26.05", "1.2.3.4", "01.2.3", "1.02.3", "1.2.03", "1.2.3-alpha.1", "1.2.3+build.1"],
)
def test_invalid_nightly_base_version_fails(tmp_path: Path, base_version: str):
    source_root = tmp_path / "source"
    write_source_tree(source_root, shared_assignment=f'platform_sdk_version = "{base_version}"')

    with pytest.raises(StampError, match="nightly base SDK version must be SemVer core"):
        stamp(
            source_root,
            cadence="nightly",
            release_label="nightly-20260512010101",
            nightly_timestamp="20260512010101",
        )


def test_invalid_nightly_timestamp_fails(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(source_root)

    with pytest.raises(StampError, match="nightly timestamp must be YYYYMMDDHHMMSS"):
        stamp(source_root, cadence="nightly", release_label="nightly-20260512", nightly_timestamp="20260512")


@pytest.mark.parametrize(
    "release_label",
    [
        "26.05-rc0",
        "1.2.3.4-rc0",
        "01.2.3-rc0",
        "1.02.3-rc0",
        "1.2.03-rc0",
        "1.2.3-alpha.1-rc0",
        "1.2.3+build.1-rc0",
        "1.0.0rc0",
    ],
)
def test_invalid_rc_label_fails(tmp_path: Path, release_label: str):
    source_root = tmp_path / "source"
    write_source_tree(source_root)

    with pytest.raises(StampError, match="RC release label must look like 1.0.0-rc0"):
        stamp(source_root, cadence="rc", release_label=release_label)


@pytest.mark.parametrize(
    "release_label",
    ["26.05", "1.2.3.4", "01.2.3", "1.02.3", "1.2.03", "1.2.3-alpha.1", "1.2.3+build.1", "1.0.0-rc0"],
)
def test_invalid_stable_label_fails(tmp_path: Path, release_label: str):
    source_root = tmp_path / "source"
    write_source_tree(source_root)

    with pytest.raises(StampError, match="stable release label must be SemVer core"):
        stamp(source_root, cadence="release", release_label=release_label)


def test_duplicate_assignment_fails(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(
        source_root,
        shared_assignment='platform_sdk_version = "2.1.0"\nplatform_sdk_version = "2.1.1"',
    )

    with pytest.raises(StampError, match="expected exactly one platform_sdk_version assignment"):
        stamp(
            source_root, cadence="nightly", release_label="nightly-20260512010101", nightly_timestamp="20260512010101"
        )


def test_missing_assignment_fails(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(source_root, sdk_assignment='__title__ = "nemo_platform"')

    with pytest.raises(StampError, match="expected exactly one __version__ assignment"):
        stamp(source_root)


def test_missing_version_file_fails(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(source_root)
    (source_root / "sdk/python/nemo-platform/src/nemo_platform/_version.py").unlink()

    with pytest.raises(StampError, match="version file is missing"):
        stamp(source_root)


def test_non_string_assignment_fails(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(source_root, shared_assignment="platform_sdk_version = 123")

    with pytest.raises(StampError, match="platform_sdk_version in .* must be a non-empty string"):
        stamp(
            source_root, cadence="nightly", release_label="nightly-20260512010101", nightly_timestamp="20260512010101"
        )


def test_cli_stamps_version(tmp_path: Path):
    source_root = tmp_path / "source"
    write_source_tree(source_root)

    status = stamp_sdk_version.main(
        [
            "--source-root",
            str(source_root),
            "--sdk-id",
            "nemo-platform",
            "--cadence",
            "release",
            "--release-label",
            "1.0.0",
        ]
    )

    assert status == 0
    assert read_versions(source_root) == ('platform_sdk_version = "1.0.0"\n', '__version__ = "1.0.0"\n')
