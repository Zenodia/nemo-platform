# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the ``config.py`` plugin config module."""

from __future__ import annotations

import pytest
from nemo_anonymizer_plugin.config import AnonymizerPluginConfig, PreviewNumRecords


def test_default_preview_num_records() -> None:
    cfg = AnonymizerPluginConfig()
    assert cfg.preview_num_records.default == 10
    assert cfg.preview_num_records.max == 10


def test_default_must_not_exceed_max() -> None:
    with pytest.raises(ValueError):
        PreviewNumRecords(max=5, default=10)
