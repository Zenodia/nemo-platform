# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch

import data_designer.config as dd
import nemo_data_designer_plugin.testing.utils as u
import pytest
from data_designer_nemo.errors import NDDInvalidConfigError
from data_designer_nemo.model_provider import (
    make_local_first_model_provider_registry,
    make_model_provider_registry,
    make_null_registry,
)


@pytest.mark.asyncio
async def test_provider_cannot_be_none() -> None:
    alias = "no-provider-specified"
    bad_model_configs = [
        dd.ModelConfig(
            alias=alias,
            model="some-model",
        )
    ]

    with (
        u.make_mock_client_context() as client_context,
        pytest.raises(NDDInvalidConfigError) as exc_info,
    ):
        await make_model_provider_registry(
            bad_model_configs, sdk=client_context.async_sdk, default_workspace=u.WORKSPACE_NAME
        )
    assert "does not have an explicit provider defined" in str(exc_info.value)


@pytest.mark.asyncio
async def test_local_first_provider_cannot_be_none() -> None:
    alias = "no-provider-specified"
    bad_model_configs = [
        dd.ModelConfig(
            alias=alias,
            model="some-model",
        )
    ]

    with u.make_mock_client_context() as client_context:
        with (
            patch("data_designer_nemo.model_provider.get_default_providers") as default_lookup,
            pytest.raises(NDDInvalidConfigError) as exc_info,
        ):
            await make_local_first_model_provider_registry(
                bad_model_configs,
                sdk=client_context.async_sdk,
                default_workspace=u.WORKSPACE_NAME,
            )

    default_lookup.assert_not_called()
    assert "explicit provider defined" in str(exc_info.value)
    assert "Missing provider(s): []" not in str(exc_info.value)


@pytest.mark.asyncio
async def test_malformed_provider_name() -> None:
    alias = "too-many-slashes"
    malformed_provider_name = "foo/bar/baz"
    bad_model_configs = [
        dd.ModelConfig(
            alias=alias,
            model="some-model",
            provider=malformed_provider_name,
        )
    ]

    with (
        u.make_mock_client_context() as client_context,
        pytest.raises(NDDInvalidConfigError) as exc_info,
    ):
        await make_model_provider_registry(
            bad_model_configs, sdk=client_context.async_sdk, default_workspace=u.WORKSPACE_NAME
        )
    assert "Malformed model provider" in str(exc_info.value)
    assert alias in str(exc_info.value)
    assert malformed_provider_name in str(exc_info.value)


@pytest.mark.asyncio
async def test_inaccessible_provider() -> None:
    inaccessible_provider_name = "inaccessible/provider"
    bad_model_configs = [
        dd.ModelConfig(
            alias="text",
            model="some-model",
            provider=inaccessible_provider_name,
        )
    ]

    with (
        u.make_mock_client_context() as client_context,
        pytest.raises(NDDInvalidConfigError) as exc_info,
    ):
        await make_model_provider_registry(
            bad_model_configs, sdk=client_context.async_sdk, default_workspace=u.WORKSPACE_NAME
        )
    assert "Cannot access provider" in str(exc_info.value)
    assert inaccessible_provider_name in str(exc_info.value)


@pytest.mark.asyncio
async def test_disallowed_model_on_provider() -> None:
    disallowed_model = "some-model-not-in-enabled-models-list"
    model_configs = [
        dd.ModelConfig(
            alias="text",
            model=disallowed_model,
            provider=u.RESTRICTED_PROVIDER_NAME,
        )
    ]

    with (
        u.make_mock_client_context() as client_context,
        u.setup_mock_providers(client_context),
        pytest.raises(NDDInvalidConfigError) as exc_info,
    ):
        await make_model_provider_registry(
            model_configs, sdk=client_context.async_sdk, default_workspace=u.WORKSPACE_NAME
        )
    assert "not enabled for provider" in str(exc_info.value)
    assert disallowed_model in str(exc_info.value)


@pytest.mark.asyncio
async def test_happy_path() -> None:
    model_configs = [
        dd.ModelConfig(
            alias="text",
            model="anything",
            provider=u.OPEN_PROVIDER_NAME,
        ),
        dd.ModelConfig(
            alias="judge",
            model=u.ENABLED_MODEL_NAME,
            provider=u.RESTRICTED_PROVIDER_NAME,
        ),
    ]

    with (
        u.make_mock_client_context() as client_context,
        u.setup_mock_providers(client_context),
    ):
        registry = await make_model_provider_registry(
            model_configs, sdk=client_context.async_sdk, default_workspace=u.WORKSPACE_NAME
        )

    assert registry is not None
    assert len(registry.providers) == 2
    expected_provider_names = {u.OPEN_PROVIDER_NAME, u.RESTRICTED_PROVIDER_NAME}
    assert expected_provider_names == {provider.name for provider in registry.providers}
    assert registry.default in expected_provider_names


@pytest.mark.asyncio
async def test_no_model_configs() -> None:
    with u.make_mock_client_context() as client_context:
        assert (
            await make_model_provider_registry([], sdk=client_context.async_sdk, default_workspace=u.WORKSPACE_NAME)
            is None
        )


def test_null_registry() -> None:
    registry = make_null_registry()

    assert len(registry.providers) == 1
    assert registry.default == "no-op"
