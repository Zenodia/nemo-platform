# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for common evaluator value types."""

from __future__ import annotations

import pytest
from nmp.evaluator.app.values import FilesetRef


class TestFilesetRefWithFragment:
    """Tests for appending path fragments to fileset references."""

    def test_appends_fragment(self) -> None:
        fileset_ref = FilesetRef(root="workspace/fileset")

        assert fileset_ref.with_fragment("validation/*.jsonl") == FilesetRef(
            root="workspace/fileset#validation/*.jsonl"
        )

    def test_strips_leading_slash(self) -> None:
        fileset_ref = FilesetRef(root="workspace/fileset")

        assert fileset_ref.with_fragment("/data/train.jsonl") == FilesetRef(root="workspace/fileset#data/train.jsonl")

    def test_rejects_empty_fragment(self) -> None:
        fileset_ref = FilesetRef(root="workspace/fileset")

        with pytest.raises(ValueError, match="fragment cannot be empty"):
            fileset_ref.with_fragment("/")

    def test_rejects_fragment_containing_delimiter(self) -> None:
        fileset_ref = FilesetRef(root="workspace/fileset")

        with pytest.raises(ValueError, match="fragment cannot contain '#'"):
            fileset_ref.with_fragment("data#train.jsonl")

    def test_rejects_existing_fragment(self) -> None:
        fileset_ref = FilesetRef(root="workspace/fileset#existing.jsonl")

        with pytest.raises(ValueError, match="already includes a fragment"):
            fileset_ref.with_fragment("validation/*.jsonl")
