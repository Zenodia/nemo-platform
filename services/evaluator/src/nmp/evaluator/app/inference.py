# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any
from urllib.parse import urlparse

from nemo_evaluator_sdk.enums import ModelFormat
from nemo_evaluator_sdk.inference import make_inference_request
from nemo_evaluator_sdk.values import Model
from nemo_platform import AsyncNeMoPlatform
from nmp.common.config import get_platform_config


async def verify_model_reachable(
    model: Model | dict[str, Any],
    sdk: AsyncNeMoPlatform,
    workspace: str,
    api_key: str | None = None,
    timeout: float | None = 10.0,
) -> dict:
    """Verify if a model is reachable by making a test request.

    Only supports 'nim' and 'openai' formats. Other formats will skip the check.

    Args:
        model: A Model object or dictionary containing model configuration (url, name, etc.).
        sdk: SDK instance with request-scoped user context.
        workspace: Workspace for resolving api_key_secret. Required.
        api_key: Optional explicit API key. If provided, overrides model.api_key.
                 If not provided, uses model.api_key or placeholder.
        timeout: Optional timeout in seconds for the test request. Defaults to 10 seconds.

    Returns:
        The response from the model endpoint, or a status dict if test was skipped.

    Raises:
        Exception: If model validation fails or model is unreachable.
    """
    # Model.model_validate() handles both dict and Model instances
    inline_model = Model.model_validate(model)

    inline_model = inline_model.with_default_headers(get_platform_headers(inline_model.url))

    # Resolve api_key_secret if present
    resolved_api_key = api_key
    if inline_model.api_key_secret:
        secret_name = inline_model.api_key_secret.root
        secret = await sdk.secrets.access(secret_name, workspace=workspace)
        resolved_api_key = secret.value

    # Only check nim and openai formats
    if inline_model.format not in (ModelFormat.NVIDIA_NIM, ModelFormat.OPEN_AI):
        return {"status": f"Test skipped for unsupported format: {inline_model.format}"}

    # Create a simple test payload with minimal tokens to reduce cost
    test_payload: dict = {
        "messages": [{"role": "user", "content": "Ping!. Answer only in one word"}],
    }

    # Check if the endpoint is a completions endpoint (not chat completions).
    # This is important to not have dependency on api version and accommodate query params.
    parsed_url = urlparse(inline_model.url)
    if parsed_url.path.endswith("/completions") and not parsed_url.path.endswith("/chat/completions"):
        test_payload = {"prompt": "Ping"}

    if inline_model.format == ModelFormat.NVIDIA_NIM:
        test_payload["max_tokens"] = 100

    # Make inference request with 2 retries, passing resolved API key
    return await make_inference_request(
        model=inline_model,
        request=test_payload,
        max_retries=3,
        api_key=resolved_api_key,
        timeout=timeout,
    )


def get_platform_headers(url: str) -> dict[str, str] | None:
    """Return evaluator service-principal headers for platform-local URLs."""
    platform_netloc = urlparse(get_platform_config().base_url).netloc
    if platform_netloc and urlparse(url).netloc == platform_netloc:
        # Include service principal header so NeMo Platform inference gateway auto-authorizes
        # this request without requiring a valid JWT Bearer token.
        return {"X-NMP-Principal-Id": "service:evaluator"}
