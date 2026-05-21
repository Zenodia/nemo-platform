# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Pytest fixtures for the IGW middleware test harnesses.

Importing :func:`igw_plugin_harness` (or :func:`igw_loopback_harness`)
into a test module — or re-exporting from a project ``conftest.py`` —
registers the fixture for the surrounding scope. Both piggyback on
``pytest_httpserver``'s function-scoped ``httpserver`` fixture so each
test gets an isolated socket and clean handler state.
"""

from collections.abc import Callable, Generator
from contextlib import ExitStack, contextmanager
from typing import cast

import pytest
from fastapi import FastAPI
from nmp.core.inference_gateway.testing.harness import IGWLoopbackHarness, IGWPluginHarness
from nmp.testing.client import ClientContext, ServiceFactory, create_test_client
from pytest_httpserver import HTTPServer


def _enable_post_response_task_tracking(client_context: ClientContext) -> None:
    """Initialise ``app.state.pending_post_response_tasks`` so ``proxy.py`` records them.

    ``proxy.py`` checks for this attribute on every request that schedules a
    fire-and-forget post-response task; production never sets it, so the
    list-or-None guard keeps the production hot path free of test-only
    state. Only the test harness initialises it here, and only the harness's
    :meth:`IGWPluginHarness.aflush_post_response` reads it.
    """
    # ``TestClient.app`` is typed as a bare ``ASGIApp`` callable but is in
    # fact our :class:`FastAPI` instance — narrow the type so ``state`` is
    # accessible.
    app = cast(FastAPI, client_context.test_client.app)
    app.state.pending_post_response_tasks = []


def _register_global_state_resets(stack: ExitStack) -> None:
    """Register IGW global-state resets so they run on fixture teardown.

    The harness's ``_cleanup`` evicts its own VMs and restores its own plugin
    registrations, but a partial cleanup (e.g. an exception in ``_build``
    before the harness is fully wired) could leave global state populated.
    Resetting all three globals on teardown guarantees the next test starts
    with empty caches and an empty registry, regardless of whether ``_cleanup``
    ran successfully.

    Each reset is independent (``_GLOBAL = None``), so execution order is
    irrelevant. Do not pair this with ``igw_mock_provider_mode=True`` in
    ``create_test_client`` — that mode already registers its own
    ``reset_global_model_cache`` callback and a double-reset is confusing
    in a debugger even though it's idempotent.
    """
    from nmp.core.inference_gateway.api.dependencies import (
        reset_global_middleware_registry,
        reset_global_model_cache,
        reset_global_virtual_model_cache,
    )

    stack.callback(reset_global_middleware_registry)
    stack.callback(reset_global_virtual_model_cache)
    stack.callback(reset_global_model_cache)


def _create_harness_client_context(
    stack: ExitStack,
    *extra_services: ServiceFactory,
) -> ClientContext:
    """Create the shared in-process IGW + Models client context for harness fixtures."""
    # Local imports keep this module cheap to import for unrelated test files.
    from nmp.core.inference_gateway.service import InferenceGatewayService
    from nmp.core.models.service import ModelsService

    service_types: list[ServiceFactory] = [InferenceGatewayService, ModelsService, *extra_services]

    _register_global_state_resets(stack)

    client_context = stack.enter_context(
        create_test_client(
            *service_types,
            client_type=ClientContext,
            igw_mock_provider_mode=False,
        )
    )
    _enable_post_response_task_tracking(client_context)

    return client_context


@contextmanager
def _igw_plugin_harness_context(
    httpserver: HTTPServer,
    *extra_services: ServiceFactory,
) -> Generator[IGWPluginHarness, None, None]:
    """IGW + Models in-process via ASGI; mock NIM via ``pytest_httpserver``.

    No uvicorn thread, no real port for IGW. The same ``pytest_httpserver``
    socket serves both the proxy step's outbound HTTP and any plugin-side
    outbound HTTP (e.g. Guardrails' rail calls).

    Includes IGW + Models by default. Pass additional service classes when a
    test needs their routes mounted in the same app.
    """
    with ExitStack() as stack:
        client_context = _create_harness_client_context(stack, *extra_services)
        harness = IGWPluginHarness._build(client_context=client_context, mock_nim=httpserver)
        stack.callback(harness._cleanup)
        yield harness


@pytest.fixture
def igw_plugin_harness(httpserver: HTTPServer) -> Generator[IGWPluginHarness, None, None]:
    with _igw_plugin_harness_context(httpserver) as harness:
        yield harness


@contextmanager
def _igw_loopback_harness_context(
    httpserver: HTTPServer,
    *extra_services: ServiceFactory,
) -> Generator[IGWLoopbackHarness, None, None]:
    """IGW + Models in-process *and* reachable on a real ``127.0.0.1:<port>``.

    Includes IGW + Models by default. Pass additional service classes when a
    test needs their routes mounted in the same app.

    See :class:`IGWLoopbackHarness` for the two-loop loop-binding caveat.

    Three things the loopback shape requires that the default doesn't:

    1. Lifecycle ordering: ASGI client owns the app's startup/shutdown,
       uvicorn comes up after the app is ready and tears down before it.
    2. Per-request ``aiohttp.ClientSession`` override — the app now runs on
       two loops (``TestClient``'s and uvicorn's). Sessions are loop-bound,
       so a singleton would fail with "attached to a different loop" on
       whichever loop didn't originate it. Production is unaffected (one
       loop per process).
    3. ``platform_config.base_url`` patched to the loopback URL so the
       plugin resolver
       (:meth:`get_openai_compatible_inference_url_and_model`) returns URLs
       reachable from the test process instead of the production default
       ``http://localhost:8080``.
    """
    from nmp.core.inference_gateway.api.dependencies import global_http_client
    from nmp.core.inference_gateway.testing._loopback import (
        override_platform_base_url,
        per_request_http_client,
        serve_app_in_thread,
    )

    with ExitStack() as stack:
        client_context = _create_harness_client_context(stack, *extra_services)

        app = cast(FastAPI, client_context.test_client.app)
        previous_override = app.dependency_overrides.get(global_http_client)
        app.dependency_overrides[global_http_client] = per_request_http_client

        def _restore_http_client_override() -> None:
            if previous_override is None:
                app.dependency_overrides.pop(global_http_client, None)
            else:
                app.dependency_overrides[global_http_client] = previous_override

        stack.callback(_restore_http_client_override)

        loopback_base_url = stack.enter_context(serve_app_in_thread(app))
        # Patch goes below uvicorn so it tears down first.
        stack.enter_context(override_platform_base_url(loopback_base_url))
        harness = cast(
            IGWLoopbackHarness,
            IGWLoopbackHarness._build(
                client_context=client_context,
                mock_nim=httpserver,
                igw_loopback_base_url=loopback_base_url,
            ),
        )
        stack.callback(harness._cleanup)
        yield harness


@pytest.fixture
def igw_loopback_harness(
    httpserver: HTTPServer,
) -> Generator[Callable[..., IGWLoopbackHarness], None, None]:
    """Factory for an IGW loopback harness.

    Call with no arguments for the default IGW + Models app:
    ``harness = igw_loopback_harness()``.

    Pass additional service classes to mount them in the same app:
    ``harness = igw_loopback_harness(GuardrailsService)``.
    """
    with ExitStack() as stack:

        def factory(*extra_services: ServiceFactory) -> IGWLoopbackHarness:
            return stack.enter_context(_igw_loopback_harness_context(httpserver, *extra_services))

        yield factory


__all__ = ["igw_plugin_harness", "igw_loopback_harness"]
