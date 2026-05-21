# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for export utility helpers."""

import pytest
from nmp.intake.app.utils.datastore import DataStoreClient
from nmp.intake.app.utils.exports import extract_nds_path


def test_extract_nds_path_returns_workspace_and_dataset():
    assert extract_nds_path("nds://default/my-dataset") == ("default", "my-dataset")


def test_extract_nds_path_error_uses_workspace_language():
    with pytest.raises(ValueError, match="nds://workspace/dataset_name"):
        extract_nds_path("nds:///missing-workspace")


def test_datastore_client_uses_intake_service_token_by_default():
    assert DataStoreClient().token == "service:intake"
