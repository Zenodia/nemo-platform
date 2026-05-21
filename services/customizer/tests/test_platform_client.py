# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from nemo_platform._exceptions import NotFoundError, PermissionDeniedError
from nmp.customizer.platform_client import check_dataset_access, fetch_model_entity
from pytest_mock import MockerFixture


def _make_sdk(mocker: MockerFixture, *, filesets_retrieve_side_effect=None, filesets_retrieve_return=None):
    """Build a mock SDK with files.filesets.retrieve wired up."""
    sdk = mocker.Mock()
    sdk.files = mocker.Mock()
    sdk.files.filesets = mocker.Mock()
    if filesets_retrieve_side_effect:
        sdk.files.filesets.retrieve = mocker.AsyncMock(side_effect=filesets_retrieve_side_effect)
    else:
        sdk.files.filesets.retrieve = mocker.AsyncMock(return_value=filesets_retrieve_return or mocker.Mock())
    return sdk


class TestCheckDatasetAccess:
    @pytest.mark.asyncio
    async def test_qualified_uri_calls_retrieve_with_parsed_workspace(self, mocker: MockerFixture) -> None:
        sdk = _make_sdk(mocker)

        await check_dataset_access(sdk, "fileset://team-b/training-data", "default")

        sdk.files.filesets.retrieve.assert_awaited_once_with(workspace="team-b", name="training-data")

    @pytest.mark.asyncio
    async def test_unqualified_name_uses_default_workspace(self, mocker: MockerFixture) -> None:
        sdk = _make_sdk(mocker)

        await check_dataset_access(sdk, "my-dataset", "default")

        sdk.files.filesets.retrieve.assert_awaited_once_with(workspace="default", name="my-dataset")

    @pytest.mark.asyncio
    async def test_raises_permission_error_on_denied(self, mocker: MockerFixture) -> None:
        sdk = _make_sdk(
            mocker,
            filesets_retrieve_side_effect=PermissionDeniedError(
                "forbidden", response=mocker.Mock(status_code=403, headers={}), body=None
            ),
        )

        with pytest.raises(PermissionError, match="Access denied to dataset fileset 'team-b/training-data'"):
            await check_dataset_access(sdk, "fileset://team-b/training-data", "default")

    @pytest.mark.asyncio
    async def test_raises_value_error_when_fileset_not_found(self, mocker: MockerFixture) -> None:
        sdk = _make_sdk(
            mocker,
            filesets_retrieve_side_effect=NotFoundError(
                "not found", response=mocker.Mock(status_code=404, headers={}), body=None
            ),
        )

        with pytest.raises(ValueError, match="Dataset fileset 'training-data' not found in workspace 'team-b'"):
            await check_dataset_access(sdk, "fileset://team-b/training-data", "default")

    @pytest.mark.asyncio
    async def test_succeeds_when_user_has_access(self, mocker: MockerFixture) -> None:
        fileset = mocker.Mock()
        sdk = _make_sdk(mocker, filesets_retrieve_return=fileset)

        await check_dataset_access(sdk, "fileset://team-b/training-data", "default")


class TestFetchModelEntity:
    @pytest.mark.asyncio
    async def test_uses_default_workspace_for_unqualified_name(self, mocker: MockerFixture) -> None:
        model_entity = mocker.Mock()
        sdk = mocker.Mock()
        sdk.models = mocker.Mock()
        sdk.models.retrieve = mocker.AsyncMock(return_value=model_entity)

        result = await fetch_model_entity("target-model", "default", sdk)

        assert result is model_entity
        sdk.models.retrieve.assert_awaited_once_with(name="target-model", workspace="default", verbose=True)

    @pytest.mark.asyncio
    async def test_uses_workspace_from_qualified_name(self, mocker: MockerFixture) -> None:
        model_entity = mocker.Mock()
        sdk = mocker.Mock()
        sdk.models = mocker.Mock()
        sdk.models.retrieve = mocker.AsyncMock(return_value=model_entity)

        result = await fetch_model_entity("team-a/target-model", "default", sdk)

        assert result is model_entity
        sdk.models.retrieve.assert_awaited_once_with(name="target-model", workspace="team-a", verbose=True)

    @pytest.mark.asyncio
    async def test_raises_permission_error_on_denied(self, mocker: MockerFixture) -> None:
        sdk = mocker.Mock()
        sdk.models = mocker.Mock()
        sdk.models.retrieve = mocker.AsyncMock(
            side_effect=PermissionDeniedError("forbidden", response=mocker.Mock(status_code=403, headers={}), body=None)
        )

        with pytest.raises(PermissionError, match="Access denied to model 'other-ws/target-model'"):
            await fetch_model_entity("other-ws/target-model", "default", sdk)

    @pytest.mark.asyncio
    async def test_raises_value_error_on_not_found_error(self, mocker: MockerFixture) -> None:
        sdk = mocker.Mock()
        sdk.models = mocker.Mock()
        sdk.models.retrieve = mocker.AsyncMock(
            side_effect=NotFoundError("not found", response=mocker.Mock(status_code=404, headers={}), body=None)
        )

        with pytest.raises(
            ValueError, match=r"Model entity not found: 'default/target-model'. Verify the model entity exists\."
        ):
            await fetch_model_entity("target-model", "default", sdk)
