# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for model check utilities with secret resolution."""

from unittest import mock

import pytest
from nemo_evaluator_sdk.values import Model
from nmp.evaluator.app.inference import verify_model_reachable


@pytest.mark.asyncio
async def test_check_model_without_secret():
    """Test model check when no secret is configured."""
    model_dict = {"url": "http://model.test/v1", "name": "test-model"}

    with mock.patch(
        "nmp.evaluator.app.inference.make_inference_request",
        new_callable=mock.AsyncMock,
    ) as mock_inference:
        mock_inference.return_value = {"status": "ok"}

        mock_sdk = mock.AsyncMock()

        try:
            await verify_model_reachable(model_dict, sdk=mock_sdk, workspace="default")
            error = None
        except Exception as e:
            error = e

        assert error is None
        mock_inference.assert_called_once()
        # Should be called without api_key parameter
        call_args = mock_inference.call_args
        assert call_args.kwargs.get("api_key") is None


@pytest.mark.asyncio
async def test_check_model_with_secret_and_workspace():
    """Test model check when secret is configured and workspace is provided."""
    model_dict = {
        "url": "http://model.test/v1",
        "name": "test-model",
        "api_key_secret": "my-secret",
    }

    mock_secret = mock.MagicMock()
    mock_secret.value = "resolved-api-key-12345"

    with mock.patch(
        "nmp.evaluator.app.inference.make_inference_request",
        new_callable=mock.AsyncMock,
    ) as mock_inference:
        mock_sdk = mock.AsyncMock()
        mock_sdk.secrets.access = mock.AsyncMock(return_value=mock_secret)
        mock_inference.return_value = {"status": "ok"}

        try:
            await verify_model_reachable(model_dict, sdk=mock_sdk, workspace="my-workspace")
            error = None
        except Exception as e:
            error = e

        assert error is None
        # Verify secret was accessed
        mock_sdk.secrets.access.assert_called_once_with("my-secret", workspace="my-workspace")
        # Verify inference was called with resolved API key
        mock_inference.assert_called_once()
        call_args = mock_inference.call_args
        assert call_args.kwargs.get("api_key") == "resolved-api-key-12345"


@pytest.mark.asyncio
async def test_check_model_with_secret_and_workspace_provided():
    """Test model check when secret is configured and workspace is provided (workspace is required)."""
    model_dict = {
        "url": "http://model.test/v1",
        "name": "test-model",
        "api_key_secret": "my-secret",
    }

    mock_sdk = mock.AsyncMock()

    with mock.patch(
        "nmp.evaluator.app.inference.make_inference_request",
        new_callable=mock.AsyncMock,
    ) as mock_inference:
        mock_inference.return_value = {"status": "ok"}

        try:
            await verify_model_reachable(model_dict, sdk=mock_sdk, workspace="my-workspace")
            error = None
        except Exception as e:
            error = e

        assert error is None
        # Should resolve secret when workspace is provided
        mock_sdk.secrets.access.assert_called_once_with("my-secret", workspace="my-workspace")
        mock_inference.assert_called_once()


@pytest.mark.asyncio
async def test_check_model_secret_resolution_failure():
    """Test model check when secret resolution fails - should propagate error."""

    from httpx import Request, Response
    from nemo_platform import NotFoundError

    model_dict = {
        "url": "http://model.test/v1",
        "name": "test-model",
        "api_key_secret": "my-secret",
    }

    mock_sdk = mock.AsyncMock()
    mock_response = Response(status_code=404, request=Request("GET", "http://test"))
    mock_sdk.secrets.access = mock.AsyncMock(
        side_effect=NotFoundError(
            message="Secret not found",
            response=mock_response,
            body={"detail": "Secret not found"},
        )
    )

    with pytest.raises(NotFoundError, match="Secret not found"):
        await verify_model_reachable(model_dict, sdk=mock_sdk, workspace="my-workspace")

    # Should attempt secret resolution
    mock_sdk.secrets.access.assert_called_once_with("my-secret", workspace="my-workspace")


@pytest.mark.asyncio
async def test_check_model_verification_failure():
    """Test model check when verification fails."""
    model_dict = {"url": "http://unreachable.test/v1", "name": "unreachable-model"}

    with mock.patch(
        "nmp.evaluator.app.inference.make_inference_request",
        new_callable=mock.AsyncMock,
    ) as mock_inference:
        verification_error = Exception("Connection refused")
        mock_inference.side_effect = verification_error

        mock_sdk = mock.AsyncMock()

        try:
            await verify_model_reachable(model_dict, sdk=mock_sdk, workspace="default")
            error = None
        except Exception as e:
            error = e

        assert error is not None
        assert error == verification_error
        mock_inference.assert_called_once()


@pytest.mark.asyncio
async def test_check_model_invalid_model_dict():
    """Test model check with invalid model dictionary."""
    model_dict = {"url": "http://model.test/v1"}  # Missing 'name' field

    mock_sdk = mock.AsyncMock()

    try:
        await verify_model_reachable(model_dict, sdk=mock_sdk, workspace="default")
        error = None
    except Exception as e:
        error = e

    assert error is not None
    # Should be a validation error from Model.model_validate
    assert isinstance(error, Exception)


@pytest.mark.asyncio
async def test_check_model_with_secret_success():
    """Test successful model check with secret resolution."""
    model_dict = {
        "url": "http://model.test/v1",
        "name": "test-model",
        "api_key_secret": "my-secret",
    }

    mock_secret = mock.MagicMock()
    mock_secret.value = "resolved-api-key-12345"

    with mock.patch(
        "nmp.evaluator.app.inference.make_inference_request",
        new_callable=mock.AsyncMock,
    ) as mock_inference:
        mock_sdk = mock.AsyncMock()
        mock_sdk.secrets.access = mock.AsyncMock(return_value=mock_secret)
        mock_inference.return_value = {"status": "ok"}

        try:
            await verify_model_reachable(model_dict, sdk=mock_sdk, workspace="my-workspace")
            error = None
        except Exception as e:
            error = e

        assert error is None
        # Verify the flow: secret access -> verify with resolved key
        mock_sdk.secrets.access.assert_called_once_with("my-secret", workspace="my-workspace")
        mock_inference.assert_called_once()
        # Verify the resolved API key was passed
        inference_call = mock_inference.call_args
        assert inference_call.kwargs["api_key"] == "resolved-api-key-12345"
        # Verify the model object was passed
        assert isinstance(inference_call.kwargs["model"], Model)
        assert inference_call.kwargs["model"].url == "http://model.test/v1"
        assert inference_call.kwargs["model"].name == "test-model"
