# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import Mock, patch
from urllib.parse import urlparse

import pytest
from nemo_evaluator_sdk.enums import ModelFormat
from nemo_evaluator_sdk.inference import make_inference_request, new_inference_client
from nemo_evaluator_sdk.values import Model
from nmp.evaluator.app.inference import get_platform_headers, verify_model_reachable


@pytest.mark.asyncio
async def test_verify_model_reachable_completions_endpoint(mock_sdk):
    """
    Test that verify_model_reachable uses 'prompt' payload for v1/completions endpoints.
    """
    from unittest.mock import AsyncMock, patch

    # Create a model with completions endpoint
    model = Model(
        url="https://api.example.com/v1/completions",
        name="test/model",
    )

    mock_response = {"status": "success", "text": "pong"}

    with patch("nmp.evaluator.app.inference.make_inference_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        # Call verify_model_reachable
        result = await verify_model_reachable(model, sdk=mock_sdk, workspace="test-workspace")

        # Verify make_inference_request was called
        assert mock_request.call_count == 1

        # Get the arguments passed to make_inference_request
        call_args = mock_request.call_args
        _, kwargs = call_args

        # Verify the request payload uses 'prompt' for completions endpoint
        request_payload = kwargs["request"]
        assert "prompt" in request_payload, "Completions endpoint should use 'prompt' in payload"
        assert request_payload["prompt"] == "Ping"
        # All models use max_tokens=100
        assert request_payload["max_tokens"] == 100, "All models should have max_tokens=100"
        assert "messages" not in request_payload, "Completions endpoint should not have 'messages'"

        # Verify the model and max_retries parameters
        assert kwargs["model"] == model
        assert kwargs["max_retries"] == 3

        # Verify the result
        assert result == mock_response


@pytest.mark.asyncio
async def test_verify_model_reachable_completions_with_query_params(mock_sdk):
    """
    Test that verify_model_reachable correctly identifies completions endpoint with query parameters.
    """
    from unittest.mock import AsyncMock, patch

    # Create a model with completions endpoint and query parameters
    model = Model(
        url="https://api.example.com/v1/completions?api-version=2024-01-01&deployment=test",
        name="test/model",
    )

    mock_response = {"status": "success"}

    with patch("nmp.evaluator.app.inference.make_inference_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        # Call verify_model_reachable
        result = await verify_model_reachable(model, sdk=mock_sdk, workspace="test-workspace")

        # Verify make_inference_request was called
        assert mock_request.call_count == 1

        # Get the request payload
        call_args = mock_request.call_args
        _, kwargs = call_args
        request_payload = kwargs["request"]

        # Verify the request uses 'prompt' for completions endpoint even with query params
        assert "prompt" in request_payload, "Completions endpoint with query params should use 'prompt'"
        assert request_payload["prompt"] == "Ping"
        # All models use max_tokens=100
        assert request_payload["max_tokens"] == 100, "All models should have max_tokens=100"
        assert "messages" not in request_payload, "Completions endpoint should not have 'messages'"

        # Verify the result
        assert result == mock_response


@pytest.mark.asyncio
async def test_verify_model_reachable_chat_completions_endpoint(mock_sdk):
    """
    Test that verify_model_reachable uses 'messages' payload for chat completions endpoints.
    """
    from unittest.mock import AsyncMock, patch

    # Create a model with chat completions endpoint
    model = Model(
        url="https://api.example.com/v1/chat/completions",
        name="test/model",
    )

    mock_response = {"status": "success", "message": "pong"}

    with patch("nmp.evaluator.app.inference.make_inference_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        # Call verify_model_reachable
        result = await verify_model_reachable(model, sdk=mock_sdk, workspace="test-workspace")

        # Verify make_inference_request was called
        assert mock_request.call_count == 1

        # Get the arguments passed to make_inference_request
        call_args = mock_request.call_args
        _, kwargs = call_args

        # Verify the request payload uses 'messages' for chat completions endpoint
        request_payload = kwargs["request"]
        assert "messages" in request_payload, "Chat completions endpoint should use 'messages' in payload"
        assert request_payload["messages"] == [{"role": "user", "content": "Ping!. Answer only in one word"}]
        # All models use max_tokens=100
        assert request_payload["max_tokens"] == 100, "All models should have max_tokens=100"
        assert "prompt" not in request_payload, "Chat completions endpoint should not have 'prompt'"

        # Verify the model and max_retries parameters
        assert kwargs["model"] == model
        assert kwargs["max_retries"] == 3

        # Verify the result
        assert result == mock_response


@pytest.mark.asyncio
async def test_verify_model_reachable_nvidia_nim_format(mock_sdk):
    """
    Test that verify_model_reachable adds max_tokens for NVIDIA NIM format.
    """
    from unittest.mock import AsyncMock, patch

    # Create a model with NVIDIA NIM format
    model = Model(
        url="https://api.example.com/v1/chat/completions",
        name="test/model",
        format=ModelFormat.NVIDIA_NIM,
    )

    mock_response = {"status": "success"}

    with patch("nmp.evaluator.app.inference.make_inference_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        # Call verify_model_reachable
        result = await verify_model_reachable(model, sdk=mock_sdk, workspace="test-workspace")

        # Verify make_inference_request was called
        assert mock_request.call_count == 1

        # Get the request payload
        call_args = mock_request.call_args
        _, kwargs = call_args
        request_payload = kwargs["request"]

        # Verify max_tokens is 100 for all models including NVIDIA NIM format
        assert "max_tokens" in request_payload, "Should include max_tokens"
        assert request_payload["max_tokens"] == 100, "All models should have max_tokens=100"
        assert "messages" in request_payload  # Should still have messages for chat endpoint

        # Verify the result
        assert result == mock_response


@pytest.mark.asyncio
async def test_verify_model_reachable_timeout_default(mock_sdk):
    """
    Test that verify_model_reachable uses default timeout of 10 seconds.
    """
    from unittest.mock import AsyncMock, patch

    model = Model(
        url="https://api.example.com/v1/chat/completions",
        name="test/model",
    )

    mock_response = {"status": "success"}

    with patch("nmp.evaluator.app.inference.make_inference_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        await verify_model_reachable(model, sdk=mock_sdk, workspace="test-workspace")

        # Verify make_inference_request was called with default timeout
        call_args = mock_request.call_args
        _, kwargs = call_args
        assert kwargs["timeout"] == 10.0, "Default timeout should be 10 seconds"


@pytest.mark.asyncio
async def test_verify_model_reachable_timeout_custom(mock_sdk):
    """
    Test that verify_model_reachable accepts custom timeout parameter.
    """
    from unittest.mock import AsyncMock, patch

    model = Model(
        url="https://api.example.com/v1/chat/completions",
        name="test/model",
    )

    mock_response = {"status": "success"}

    with patch("nmp.evaluator.app.inference.make_inference_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        await verify_model_reachable(model, sdk=mock_sdk, workspace="test-workspace", timeout=5.0)

        # Verify make_inference_request was called with custom timeout
        call_args = mock_request.call_args
        _, kwargs = call_args
        assert kwargs["timeout"] == 5.0, "Custom timeout should be passed through"


@pytest.mark.asyncio
async def test_make_inference_request_timeout_passed_to_client():
    """
    Test that make_inference_request passes timeout to client.with_options().
    """
    from unittest.mock import AsyncMock, patch

    from openai.types.chat import ChatCompletion, ChatCompletionMessage
    from openai.types.chat.chat_completion import Choice

    model = Model(
        url="https://api.example.com/v1/chat/completions",
        name="test/model",
    )

    mock_chat_completion = ChatCompletion(
        id="test-id",
        object="chat.completion",
        created=1234567890,
        model="test/model",
        choices=[
            Choice(
                index=0,
                message=ChatCompletionMessage(role="assistant", content="test response"),
                finish_reason="stop",
            )
        ],
    )

    with patch("nemo_evaluator_sdk.inference.AsyncOpenAI.chat") as mock_chat:
        mock_chat.completions.create = AsyncMock(return_value=mock_chat_completion)
        client = new_inference_client(model)

        request = {"messages": [{"role": "user", "content": "test"}]}
        await make_inference_request(model, request, timeout=15.0, client=client)

        # Verify with_options was called with timeout
        assert client.max_retries == 0
        mock_chat.completions.create.assert_called_once()
        call_kwargs = mock_chat.completions.create.call_args[1]
        assert call_kwargs["timeout"] == 15.0, "Timeout should be passed to create"


class _InferenceTransportTestMixin:
    PLATFORM_BASE_URL = "http://nemo-platform-api.default.svc.cluster.local"
    EXTERNAL_URL = "http://external-inference-server.example.com/v1"

    def _make_mock_completion(self):
        from openai.types.chat import ChatCompletion, ChatCompletionMessage
        from openai.types.chat.chat_completion import Choice

        return ChatCompletion(
            id="test-id",
            object="chat.completion",
            created=1234567890,
            model="test/model",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(role="assistant", content="test response"),
                    finish_reason="stop",
                )
            ],
        )


class TestGetPlatformHeaders(_InferenceTransportTestMixin):
    """Tests for deriving evaluator service-principal headers from a model URL."""

    def test_includes_service_principal_header_for_platform_url(self):
        """Platform-local model URLs should resolve to evaluator service-principal headers."""
        with patch("nmp.evaluator.app.inference.get_platform_config") as mock_config:
            mock_config.return_value = Mock(base_url=self.PLATFORM_BASE_URL)

            headers = get_platform_headers(f"{self.PLATFORM_BASE_URL}/v1/chat/completions")

        assert headers == {"X-NMP-Principal-Id": "service:evaluator"}

    def test_omits_service_principal_header_for_url_containing_platform_hostname_as_substring(self):
        """Hostnames that only contain the platform hostname as a substring must not match."""
        platform_netloc = urlparse(self.PLATFORM_BASE_URL).netloc
        spoofed_url = f"http://evil.{platform_netloc}/v1/chat/completions"

        with patch("nmp.evaluator.app.inference.get_platform_config") as mock_config:
            mock_config.return_value = Mock(base_url=self.PLATFORM_BASE_URL)

            headers = get_platform_headers(spoofed_url)

        assert headers is None

    def test_omits_service_principal_header_for_external_url(self):
        """External model URLs should not resolve to evaluator service-principal headers."""
        with patch("nmp.evaluator.app.inference.get_platform_config") as mock_config:
            mock_config.return_value = Mock(base_url=self.PLATFORM_BASE_URL)

            headers = get_platform_headers(f"{self.EXTERNAL_URL}/chat/completions")

        assert headers is None


class TestMakeInferenceRequestDefaultHeaders(_InferenceTransportTestMixin):
    """Tests for forwarding effective request headers through the SDK transport."""

    @pytest.mark.asyncio
    async def test_forwards_model_default_headers_as_extra_headers(self):
        """Model-level default headers should be attached to the outgoing request."""
        from unittest.mock import AsyncMock, patch

        model = Model(
            url=f"{self.PLATFORM_BASE_URL}/v1/chat/completions",
            name="test/model",
            default_headers={"X-NMP-Principal-Id": "service:evaluator"},
        )

        with patch("nemo_evaluator_sdk.inference.AsyncOpenAI.chat") as mock_chat:
            mock_chat.completions.create = AsyncMock(return_value=self._make_mock_completion())

            await make_inference_request(model, {"messages": [{"role": "user", "content": "hi"}]})

            request_body = mock_chat.completions.create.call_args.kwargs
            assert request_body["extra_headers"] == {"X-NMP-Principal-Id": "service:evaluator"}

    @pytest.mark.asyncio
    async def test_merges_model_and_per_call_default_headers(self):
        """Per-call headers should merge with model-level headers and override on collision."""
        from unittest.mock import AsyncMock, patch

        model = Model(
            url=f"{self.PLATFORM_BASE_URL}/v1/chat/completions",
            name="test/model",
            default_headers={"X-NMP-Principal-Id": "service:evaluator", "X-Trace-Id": "model"},
        )

        with patch("nemo_evaluator_sdk.inference.AsyncOpenAI.chat") as mock_chat:
            mock_chat.completions.create = AsyncMock(return_value=self._make_mock_completion())

            await make_inference_request(
                model,
                {"messages": [{"role": "user", "content": "hi"}]},
                default_headers={"X-Trace-Id": "request", "X-Request-Id": "abc"},
            )

            request_body = mock_chat.completions.create.call_args.kwargs
            assert request_body["extra_headers"] == {
                "X-NMP-Principal-Id": "service:evaluator",
                "X-Trace-Id": "request",
                "X-Request-Id": "abc",
            }


@pytest.mark.asyncio
async def test_make_inference_request_timeout_none_uses_default():
    """
    Test that make_inference_request does not pass timeout when None (uses client default).
    """
    from unittest.mock import AsyncMock, patch

    from openai.types.chat import ChatCompletion, ChatCompletionMessage
    from openai.types.chat.chat_completion import Choice

    model = Model(
        url="https://api.example.com/v1/chat/completions",
        name="test/model",
    )

    mock_chat_completion = ChatCompletion(
        id="test-id",
        object="chat.completion",
        created=1234567890,
        model="test/model",
        choices=[
            Choice(
                index=0,
                message=ChatCompletionMessage(role="assistant", content="test response"),
                finish_reason="stop",
            )
        ],
    )

    with patch("nemo_evaluator_sdk.inference.AsyncOpenAI.chat") as mock_chat:
        mock_chat.completions.create = AsyncMock(return_value=mock_chat_completion)
        client = new_inference_client(model)

        request = {"messages": [{"role": "user", "content": "test"}]}
        await make_inference_request(model, request, timeout=None, client=client)

        # Verify with_options was called without timeout (only max_retries)
        mock_chat.completions.create.assert_called_once()
        call_kwargs = mock_chat.completions.create.call_args[1]
        assert "timeout" not in call_kwargs, "Timeout should not be passed when None"
        assert client.max_retries == 0, "max_retries should still be passed"
