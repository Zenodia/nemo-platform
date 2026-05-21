# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from nmp.evaluator.app.datasets.fileset_selectors import (
    fileset_glob_prefix_dir,
    is_fileset_glob_pattern,
    list_matching_fileset_paths,
    matches_fileset_glob,
)


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ("*.json", True),
        ("**/*.json", True),
        ("file?.json", True),
        ("file[0-9].json", True),
        ("validation/file?.jsonl", True),
        ("validation/file[ab].jsonl", True),
        ("train.jsonl", False),
        ("data/train.json", False),
        ("validation/file.jsonl", False),
        ("", False),
    ],
)
def test_is_fileset_glob_pattern(pattern: str, expected: bool):
    assert is_fileset_glob_pattern(pattern) is expected


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ("*.json", ""),
        ("**/*.json", ""),
        ("data/*.json", "data"),
        ("data/**/train*.jsonl", "data"),
        ("/data/*.json", "data"),
        ("subdir/nested.json", "subdir/nested.json"),
    ],
)
def test_fileset_glob_prefix_dir(pattern: str, expected: str):
    assert fileset_glob_prefix_dir(pattern) == expected


def test_matches_fileset_glob_is_root_anchored():
    assert matches_fileset_glob("validation/a.jsonl", "validation/*.jsonl") is True
    assert matches_fileset_glob("nested/validation/a.jsonl", "validation/*.jsonl") is False
    assert matches_fileset_glob("validation/nested/a.jsonl", "validation/*.jsonl") is False
    assert matches_fileset_glob("validation/nested/a.jsonl", "validation/**/*.jsonl") is True


@pytest.mark.parametrize(
    ("filepath", "pattern", "expected"),
    [
        ("train.json", "*.json", True),
        ("test.json", "*.json", True),
        ("data.jsonl", "*.json", False),
        ("train.json", "train.json", True),
        ("test.json", "train.json", False),
        ("file1.json", "file?.json", True),
        ("file10.json", "file?.json", False),
        ("file1.json", "file[0-9].json", True),
        ("filea.json", "file[0-9].json", False),
        ("subdir/nested.json", "*.json", False),
        ("data/train.json", "*.json", False),
        ("subdir/nested.json", "subdir/*.json", True),
        ("nested/subdir/nested.json", "subdir/*.json", False),
        ("subdir/nested.json", "other/*.json", False),
        ("data/train.json", "*/*.json", True),
        ("nested/data/train.json", "*/*.json", False),
        ("nested/data/train.json", "**/*.json", True),
    ],
)
def test_matches_fileset_glob(filepath: str, pattern: str, expected: bool):
    assert matches_fileset_glob(filepath, pattern) is expected


@pytest.mark.asyncio
async def test_list_matching_fileset_paths_filters_by_glob():
    sdk = AsyncMock()
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="validation/a.jsonl"),
            SimpleNamespace(path="validation/b.jsonl"),
            SimpleNamespace(path="train/c.jsonl"),
        ]
    )

    matched = await list_matching_fileset_paths(
        sdk,
        workspace="workspace",
        fileset_name="fileset",
        fragment_pattern="validation/*.jsonl",
    )

    assert matched == ["validation/a.jsonl", "validation/b.jsonl"]
    sdk.files.list.assert_awaited_once_with(
        fileset="fileset",
        workspace="workspace",
        remote_path="validation/",
    )


@pytest.mark.asyncio
async def test_list_matching_fileset_paths_returns_sorted_matches():
    sdk = AsyncMock()
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="validation/b.jsonl"),
            SimpleNamespace(path="validation/a.jsonl"),
            SimpleNamespace(path="validation/c.jsonl"),
        ]
    )

    matched = await list_matching_fileset_paths(
        sdk,
        workspace="workspace",
        fileset_name="fileset",
        fragment_pattern="validation/*.jsonl",
    )

    assert matched == ["validation/a.jsonl", "validation/b.jsonl", "validation/c.jsonl"]


@pytest.mark.asyncio
async def test_list_matching_fileset_paths_rejects_too_many_matches():
    sdk = AsyncMock()
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="validation/a.jsonl"),
            SimpleNamespace(path="validation/b.jsonl"),
            SimpleNamespace(path="validation/c.jsonl"),
        ]
    )

    with pytest.raises(ValueError, match="matched more than 2 validation targets"):
        await list_matching_fileset_paths(
            sdk,
            workspace="workspace",
            fileset_name="fileset",
            fragment_pattern="validation/*.jsonl",
            max_validation_targets=2,
        )


@pytest.mark.asyncio
async def test_list_matching_fileset_paths_supports_question_mark_patterns():
    sdk = AsyncMock()
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="validation/file1.jsonl"),
            SimpleNamespace(path="validation/file12.jsonl"),
            SimpleNamespace(path="validation/fileA.jsonl"),
        ]
    )

    matched = await list_matching_fileset_paths(
        sdk,
        workspace="workspace",
        fileset_name="fileset",
        fragment_pattern="validation/file?.jsonl",
    )

    assert matched == ["validation/file1.jsonl", "validation/fileA.jsonl"]


@pytest.mark.asyncio
async def test_list_matching_fileset_paths_supports_character_class_patterns():
    sdk = AsyncMock()
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="validation/filea.jsonl"),
            SimpleNamespace(path="validation/fileb.jsonl"),
            SimpleNamespace(path="validation/filec.jsonl"),
        ]
    )

    matched = await list_matching_fileset_paths(
        sdk,
        workspace="workspace",
        fileset_name="fileset",
        fragment_pattern="validation/file[ab].jsonl",
    )

    assert matched == ["validation/filea.jsonl", "validation/fileb.jsonl"]


@pytest.mark.asyncio
async def test_list_matching_fileset_paths_simple_pattern_does_not_match_nested_paths():
    sdk = AsyncMock()
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="root.jsonl"),
            SimpleNamespace(path="nested/root.jsonl"),
        ]
    )

    matched = await list_matching_fileset_paths(
        sdk,
        workspace="workspace",
        fileset_name="fileset",
        fragment_pattern="*.jsonl",
    )

    assert matched == ["root.jsonl"]


@pytest.mark.asyncio
async def test_list_matching_fileset_paths_path_pattern_does_not_match_from_right():
    sdk = AsyncMock()
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="validation/root.jsonl"),
            SimpleNamespace(path="nested/validation/root.jsonl"),
        ]
    )

    matched = await list_matching_fileset_paths(
        sdk,
        workspace="workspace",
        fileset_name="fileset",
        fragment_pattern="validation/*.jsonl",
    )

    assert matched == ["validation/root.jsonl"]


@pytest.mark.asyncio
async def test_list_matching_fileset_paths_lists_prefix_for_recursive_glob():
    sdk = AsyncMock()
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="validation/root.jsonl"),
            SimpleNamespace(path="validation/nested/root.jsonl"),
            SimpleNamespace(path="train/root.jsonl"),
        ]
    )

    matched = await list_matching_fileset_paths(
        sdk,
        workspace="workspace",
        fileset_name="fileset",
        fragment_pattern="validation/**/*.jsonl",
    )

    assert matched == ["validation/nested/root.jsonl", "validation/root.jsonl"]
    sdk.files.list.assert_awaited_once_with(
        fileset="fileset",
        workspace="workspace",
        remote_path="validation/",
    )


@pytest.mark.asyncio
async def test_list_matching_fileset_paths_exact_path_without_glob_matches_only_exact_path():
    sdk = AsyncMock()
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="validation/a.jsonl"),
            SimpleNamespace(path="validation/a.jsonl.bak"),
            SimpleNamespace(path="train/a.jsonl"),
        ]
    )

    matched = await list_matching_fileset_paths(
        sdk,
        workspace="workspace",
        fileset_name="fileset",
        fragment_pattern="validation/a.jsonl",
    )

    assert matched == ["validation/a.jsonl"]


@pytest.mark.asyncio
async def test_list_matching_fileset_paths_ignores_entries_without_string_path():
    sdk = AsyncMock()
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path=None),
            SimpleNamespace(path=123),
            SimpleNamespace(other="missing-path"),
            SimpleNamespace(path="validation/a.jsonl"),
        ]
    )

    matched = await list_matching_fileset_paths(
        sdk,
        workspace="workspace",
        fileset_name="fileset",
        fragment_pattern="validation/*.jsonl",
    )

    assert matched == ["validation/a.jsonl"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "list_response",
    [
        SimpleNamespace(),
        SimpleNamespace(data=None),
    ],
)
async def test_list_matching_fileset_paths_handles_missing_or_none_data(list_response: SimpleNamespace):
    sdk = AsyncMock()
    sdk.files.list.return_value = list_response

    matched = await list_matching_fileset_paths(
        sdk,
        workspace="workspace",
        fileset_name="fileset",
        fragment_pattern="validation/*.jsonl",
    )

    assert matched == []
