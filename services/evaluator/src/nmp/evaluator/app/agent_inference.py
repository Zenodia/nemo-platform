# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Service-layer agent inference wrapper.

Re-exports the SDK-level agent inference functions and adds service-specific
utilities such as ``verify_agent_reachable``.
"""

from typing import Any

from nemo_evaluator_sdk.agent_inference import make_agent_inference_request
from nemo_evaluator_sdk.enums import AgentFormat
from nemo_evaluator_sdk.values.agents import Agent
from nemo_platform import AsyncNeMoPlatform


async def verify_agent_reachable(
    agent: Agent | dict[str, Any],
    sdk: AsyncNeMoPlatform,
    workspace: str,
    api_key: str | None = None,
    timeout: float | None = 10.0,
) -> dict:
    """Verify if an agent endpoint is reachable by making a lightweight test request.

    For NAT agents, sends a minimal ``/generate/full`` request.
    For generic agents, the check is skipped (no standard health endpoint).

    Args:
        agent: An Agent object or dictionary containing agent configuration.
        sdk: SDK instance with request-scoped user context.
        workspace: Workspace for resolving api_key_secret.
        api_key: Optional explicit API key.
        timeout: Optional timeout in seconds. Defaults to 10 seconds.

    Returns:
        The response from the agent endpoint, or a status dict if test was skipped.
    """
    inline_agent = Agent.model_validate(agent)

    # Resolve api_key_secret if present
    resolved_api_key = api_key
    if inline_agent.api_key_secret:
        secret_name = inline_agent.api_key_secret.root
        secret = await sdk.secrets.access(secret_name, workspace=workspace)
        resolved_api_key = secret.value

    if inline_agent.format == AgentFormat.GENERIC:
        return {"status": "Test skipped for generic agent format (no standard health endpoint)"}

    # NAT agent: do a lightweight inference request
    # TODO: Payload of format: payload = {"input_message": input_message}
    # Check https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/develop/examples/evaluation_and_profiling/simple_web_query_eval/src/nat_simple_web_query_eval/scripts/evaluate_single_item_simple.py
    # Check if there generic health check of NAT agents.
    test_request = {"input_message": "ping"}

    return await make_agent_inference_request(
        agent=inline_agent,
        request=test_request,
        max_retries=1,
        api_key=resolved_api_key,
        timeout=timeout,
    )
