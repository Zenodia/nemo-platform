# IGW Middleware Plugin Test Harness

Integration test infrastructure for `NemoInferenceMiddleware` plugins.

Tests exercise the real IGW + Models request pipeline against a single
`pytest_httpserver` socket that stands in for the upstream NIM. Plugin
code (`process_request`, `process_response`, `process_post_response`)
runs with its production implementation — the only mock is the upstream
model provider itself, which every offline test needs.

## Quick start

### 1. Re-export the fixture in your plugin's `conftest.py`

```python
# plugins/<your-plugin>/tests/integration/conftest.py
from nmp.core.inference_gateway.testing.fixtures import igw_plugin_harness

__all__ = ["igw_plugin_harness"]
```

### 2. Write a test

```python
from nmp.core.inference_gateway.testing.harness import IGWPluginHarness
from nmp.testing.mock_chat_completions import ChatCompletion, chat_completion


def test_safe_input_reaches_backend(igw_plugin_harness: IGWPluginHarness) -> None:
    h = igw_plugin_harness

    # Queue a canned response for the upstream model.
    h.mock_chat_completions("my-model", responses=[ChatCompletion(body=chat_completion(content="Hello!"))])

    # Create a provider whose host_url points at the mock NIM.
    h.add_provider(workspace="default", served_models={"my-model": "my-model"})

    # Register your plugin and create a VirtualModel that uses it.
    with h.load_plugin("nemo-my-plugin"):
        h.add_virtual_model(
            workspace="default",
            name="my-vm",
            default_model_entity="default/my-model",
            request_middleware=[{"name": "nemo-my-plugin", "config_type": "...", "config": {}}],
        )

        response = h.chat_completions(
            workspace="default",
            body={"model": "my-vm", "messages": [{"role": "user", "content": "hi"}]},
        )

    h.assert_called_once("my-model")
    assert response["choices"][0]["message"]["content"] == "Hello!"
```

### 3. Choose a fixture

| Fixture | When to use |
|---|---|
| `igw_plugin_harness` | Default. No real port for IGW; plugin outbound HTTP goes directly to the mock NIM via `nim_base_url`. |
| `igw_loopback_harness` | Factory for tests where plugin outbound HTTP needs to traverse IGW (e.g. the plugin calls `get_openai_compatible_inference_url_and_model` and the resulting URL must be reachable). Call `h = igw_loopback_harness()`, which includes IGW + Models by default, or pass extra service classes like `igw_loopback_harness(GuardrailsService)` to mount additional routes. Costs a uvicorn thread + per-request `aiohttp.ClientSession` override. |

### 4. Choose a plugin registration method

| Method | When to use |
|---|---|
| `load_plugin(name)` | Plugin is pip-installed. Discovers via the `nemo.inference_middleware` entry-point group — same path as production. **Preferred.** |
| `use_plugin(name, instance)` | Plugin is not installable (workspace-only), or you need a `MagicMock(spec=...)`. |

Both default to `call_lifecycle=True` (runs `on_startup` / `on_shutdown`).
Async variants: `aload_plugin`, `ause_plugin`.

## What is real

These run the same code as production:

1. **IGW + Models FastAPI apps** — same constructors, routers, dependency wiring.
2. **Full IGW request pipeline** — `virtual_model_proxy` → request middleware → proxy step → response middleware → post-response fire-and-forget.
3. **Plugin code** — `process_request` / `process_response` / `process_post_response` are the production methods.
4. **Real HTTP from IGW to the upstream** — `aiohttp` connects to `pytest_httpserver` over a real socket. Header dropping, body framing, content-length all behave as in production.
5. **Real HTTP from plugin outbound calls** — plugin-originated requests (e.g. Guardrails' rail calls) terminate at the same socket.
6. **SDK clients** — `NeMoPlatform` (sync) and `AsyncNeMoPlatform` (async) via `httpx.ASGITransport`.
7. **Entity store** — in-memory; entities created via the SDK persist and are read back during cache refreshes.
8. **Cache refresh** — `refresh_virtual_model_cache` and `refresh_model_cache` with real implementations.
9. **Middleware config pre-resolution** — `validate_middleware_config` runs for every VM with middleware entries.

## What is mocked or substituted

1. **The upstream NIM** — `MockChatCompletionsHandler` serves canned responses. The only unavoidable mock.
2. **SDK transport** — `httpx.ASGITransport` (no real port for IGW). The loopback variant adds a real port.
3. **Plugin discovery** — bypassed when using `use_plugin`. Use `load_plugin` for production parity.
4. **`get_platform_config()`** — patched in the loopback variant so the resolver returns the loopback URL.
5. **`global_http_client`** — replaced with per-request sessions in the loopback variant (loop-binding workaround).
6. **Passthrough VM auto-creation** — the `provider_reconciler` doesn't run. Tests needing the resolver must create passthrough VMs manually.
7. **Background cache-refresh task** — tests refresh synchronously inside `add_provider` / `add_virtual_model`.
8. **Authorization** — disabled by default (`auth_enabled=False`).

## What cannot be tested

- **Multi-worker cache consistency** — caches are process-local globals.
- **Production-typical timings** — cache cold-start, background refresh races.
- **Real upstream error shapes** — real NIMs return varying error envelopes; the mock returns controlled shapes.
- **OPA / authz** — disabled by default; no integration test exercises it.
- **Rate limiting, retries, circuit breaking** — none of these layers exist in the harness.

## API reference

### Setup

| Method | Description |
|---|---|
| `add_provider(workspace, served_models, ...)` | Register a `ModelProvider` routed at the mock NIM. Call **before** `add_virtual_model`. |
| `add_virtual_model(workspace, name, ...)` | Create a `VirtualModel` and refresh caches so it routes immediately. |
| `mock_chat_completions(model, responses)` | Queue mock responses for a model. Responses are consumed in order; the last is reused if drained. |
| `load_plugin(name)` / `use_plugin(name, instance)` | Register a plugin (context manager). |
| `refresh_caches()` | Full model + VM cache refresh. Needed when `api_key_secret_name` is set on a provider. |

### Inference

| Method | Description |
|---|---|
| `chat_completions(workspace, body)` | Non-streaming chat completion via the SDK. |
| `stream_chat_completions(workspace, body)` | Streaming chat completion. Returns parsed SSE chunks (`list[dict]`) for `text/event-stream` responses, or the raw JSON body (`dict`) when a plugin short-circuits with an immediate response. |
| `achat_completions(workspace, body)` | Async sibling of `chat_completions`. |

### Assertions

| Method | Description |
|---|---|
| `assert_called_once(model)` | Model received exactly one request. |
| `assert_call_count(model, n)` | Model received exactly `n` requests. |
| `assert_no_calls_to(model)` | Model received zero requests. |
| `assert_call_order([m1, m2, ...])` | Models were called in this exact sequence. |
| `assert_request_messages_contain(model, substring, *, index=0)` | The `index`-th request's messages contain `substring`. |
| `assert_request_body_for(model, predicate, *, index=0)` | `predicate(body)` is true for the `index`-th request. |
| `assert_request_path_for(model, path, *, index=0)` | The `index`-th request arrived on `path`. |
| `assert_request_headers_contain(model, header, value=None, *, index=0)` | The `index`-th request carries `header` (optionally matching `value`). |
| `requests_for(model)` | Return all `RecordedRequest` objects for `model`. |

### Post-response

| Method | Description |
|---|---|
| `aflush_post_response()` | Await all fire-and-forget post-response tasks scheduled so far. Must be called from an async test after `achat_completions`. |

### Mock response types

Defined in `nmp.testing.mock_chat_completions`:

| Type | Description |
|---|---|
| `ChatCompletion(body, status_code=200)` | Non-streaming JSON response. |
| `ChatCompletionStream(chunks, status_code=200)` | Streaming SSE response. |
| `ErrorResponse(status_code, body)` | Error response (status >= 400). |
| `chat_completion(content, model, ...)` | Builder for a non-streaming response body. |
| `chat_completion_chunk(content, model, ...)` | Builder for a single SSE chunk body. |

## File layout

```
nmp.core.inference_gateway.testing/
├── harness.py        # IGWPluginHarness, IGWLoopbackHarness
├── fixtures.py       # igw_plugin_harness, igw_loopback_harness (pytest fixtures)
├── _loopback.py      # serve_app_in_thread, per_request_http_client, override_platform_base_url
└── README.md         # this file

nmp.testing/
└── mock_chat_completions.py   # MockChatCompletionsHandler, ChatCompletion, ChatCompletionStream, etc.
```
