# Intake Service

**The front door for LLM data in the NeMo Flywheel platform**

## Overview

Intake is a microservice that stores LLM entries and user feedback, providing a stable HTTP API and normalized data model for the entire NeMo platform. It follows Entity Store patterns with async-first architecture, comprehensive filtering, and namespace-scoped resources.

## What it stores

- **Apps** - Applications that produce entries (namespace-scoped)
- **Tasks** - Specific tasks within apps (e.g., chat, completion)
- **Entries** - Full LLM interactions (request + response + context + feedback)
- **Events** - User feedback and actions on entries

## Quick Example

```bash
# Store an entry (app and task will be auto-created if needed)
curl -X POST http://localhost:8080/v1/intake/entries \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "chatcmpl-abc123",
    "namespace": "default",
    "data": {
      "request": {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "What is 2+2?"}]
      },
      "response": {
        "choices": [{"message": {"role": "assistant", "content": "4"}}]
      }
    },
    "context": {
      "app": "default/my-app",
      "task": "chat",
      "thread_id": "conv_123"
    }
  }'

# Get entry by external_id
curl http://localhost:8080/v1/intake/entries/external:chatcmpl-abc123

# Add user feedback
curl -X POST http://localhost:8080/v1/intake/entries/external:chatcmpl-abc123/events \
  -H "Content-Type: application/json" \
  -d '{
    "events": [{
      "event_type": "user_feedback",
      "thumb": "up"
    }]
  }'
```

## API Endpoints

### Apps

- `GET /v1/intake/apps` - List apps with filter/search
- `POST /v1/intake/apps` - Create app
- `GET /v1/intake/apps/{namespace}/{app_name}` - Get app
- `PATCH /v1/intake/apps/{namespace}/{app_name}` - Update app
- `DELETE /v1/intake/apps/{namespace}/{app_name}` - Delete app

### Tasks (sub-resources of Apps)

- `GET /v1/intake/apps/{namespace}/{app_name}/tasks` - List tasks for app
- `POST /v1/intake/apps/{namespace}/{app_name}/tasks` - Create task
- `GET /v1/intake/apps/{namespace}/{app_name}/tasks/{task_name}` - Get task
- `PATCH /v1/intake/apps/{namespace}/{app_name}/tasks/{task_name}` - Update task
- `DELETE /v1/intake/apps/{namespace}/{app_name}/tasks/{task_name}` - Delete task

### Entries

- `GET /v1/intake/entries` - List/search entries with advanced filtering
- `POST /v1/intake/entries` - Create entry (auto-registers app/task if needed)
- `GET /v1/intake/entries/{entry_id}` - Get entry by ID
- `GET /v1/intake/entries/external:{external_id}` - Get entry by external_id
- `PATCH /v1/intake/entries/{entry_id}` - Update entry
- `DELETE /v1/intake/entries/{entry_id}` - Delete entry
- `POST /v1/intake/entries/{entry_id}/events` - Add events to entry
- `DELETE /v1/intake/entries/{entry_id}/events/{event_id}` - Delete event

## Key Features

- **Auto-registration**: Apps and tasks are automatically created when entries reference them
- **ID and external_id**: All entries get an auto-generated `id` (e.g., `entry-abc123`). You can optionally provide an `external_id` for your own reference IDs
- **external_id pattern**: Use `external:` prefix to reference entries by client-provided IDs (e.g., `/v1/intake/entries/external:chatcmpl-abc123`)
- **Namespace-scoped**: All resources are scoped by namespace for multi-tenancy
- **Advanced filtering**: Filter entries by namespace, app, task, thread_id, feedback, timestamps
- **Thread aggregation**: Use `longest_per_thread=true` filter to get only the longest entry per thread
- **Async-first**: All operations use async/await for better performance

## Architecture

- **Database**: PostgreSQL (primary storage) or SQLite (for testing)
- **Framework**: FastAPI with async endpoints
- **Persistence**: nmp_persistence EntityStorage interface
- **Data Model**: Entities defined in nmp_common
- **Deployment**: Docker container with uvicorn

## Development

Run these commands from the repository root unless a command says otherwise.
Intake tests rely on shared platform test helpers, so use the root `uv`
environment instead of package-scoped `uv run --package ...` commands.

### Intake Bootstrap

```bash
make clean-python
make bootstrap-python PYTORCH_DEPS=cpu
make update-sdk
```

Run `make update-sdk` after Intake route, schema, OpenAPI, or Stainless changes.
It refreshes the OpenAPI output, Stainless config, web SDK, and generated CLI
surface.

`make update-sdk` and the Stainless step in `make lint-fix` require
`STAINLESS_API_KEY`. If the key is missing or Stainless does not pull the
regenerated Python SDK, CLI generation will log missing
`nemo_platform.resources.intake` imports because the checked-in SDK is still
behind the updated `sdk/stainless.yaml`.

### Test Intake

```bash
make test-service SERVICE=intake
uv run --frozen pytest packages/nmp_platform_runner/tests -q
uv run --frozen pytest services/core/auth/tests/test_embedded_pdp.py -q
```

For a narrower Intake-only loop:

```bash
uv run --frozen pytest \
  services/intake/tests/test_entries.py \
  services/intake/tests/test_exports.py \
  services/intake/tests/test_export_utils.py \
  -q
```

For a narrower registry/auth loop:

```bash
uv run --frozen pytest \
  packages/nmp_platform_runner/tests/test_registry.py \
  packages/nmp_platform_runner/tests/test_config.py \
  services/core/auth/tests/test_embedded_pdp.py \
  -q
```

### Run Intake Locally

Start the platform runner with Intake and the core services it depends on:

```bash
uv run nemo services run \
  --services auth,entities,intake \
  --host 127.0.0.1 \
  --port 8080
```

The bundled local runner config disables auth by default. For a quick API smoke
test:

```bash
BASE=http://127.0.0.1:8080

curl -i -X POST "$BASE/apis/entities/v2/workspaces" \
  -H 'Content-Type: application/json' \
  -d '{"name":"default"}'

curl -i -X POST "$BASE/apis/intake/v2/workspaces/default/apps" \
  -H 'Content-Type: application/json' \
  -d '{"name":"test-app","description":"Local test app"}'

curl -i -X POST "$BASE/apis/intake/v2/workspaces/default/apps/test-app/tasks" \
  -H 'Content-Type: application/json' \
  -d '{"name":"chat","description":"Local chat task"}'

curl -i -X POST "$BASE/apis/intake/v2/workspaces/default/entries" \
  -H 'Content-Type: application/json' \
  -d '{
    "external_id": "local-entry-1",
    "data": {
      "request": {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "What is 2+2?"}]
      },
      "response": {
        "choices": [{"message": {"role": "assistant", "content": "4"}}]
      }
    },
    "context": {
      "app": "default/test-app",
      "task": "chat",
      "thread_id": "local-thread-1"
    }
  }'

curl -i "$BASE/apis/intake/v2/workspaces/default/entries"
```

### Run Spans POC Locally

Prerequisites:

- Run from the repository root with the uv workspace synced.
- Docker must be running for the local ClickHouse container.
- The local service command below starts Auth, Entities, and Intake because Intake routes depend on platform auth context.

Start ClickHouse for the spans POC:

```bash
services/intake/scripts/spans/run_clickhouse.sh
```

Intake can start without ClickHouse. In that mode the existing Intake routes remain available, while the spans/trace ingest routes return 503 until ClickHouse is running and the first trace request can initialize the schema.

Run Intake, then send a sample OTLP trace:

```bash
uv run nemo services run \
  --services auth,entities,intake \
  --host 127.0.0.1 \
  --port 8000

uv run services/intake/examples/send_otel_sample.py

curl -i "http://127.0.0.1:8000/apis/intake/v2/workspaces/default/spans?filter[session_id]=sample-session"
```

Run a minimal LangChain agent with OpenInference instrumentation:

```bash
export OPENAI_API_KEY="..."

uv run --package nmp-intake \
  --with 'langchain>=1.0.0' \
  --with 'langchain-openai>=1.1.14' \
  --with 'openinference-instrumentation-langchain>=0.1.63' \
  services/intake/examples/send_langchain_openinference_agent.py \
  --endpoint "http://127.0.0.1:8000/apis/intake/v2/workspaces/default/ingest/otlp/v1/traces"

curl -i "http://127.0.0.1:8000/apis/intake/v2/workspaces/default/spans?filter[session_id]=langchain-openinference-smoke"
```

### Test Permissions Locally

Create a small auth-enabled local config:

```bash
mkdir -p tmp
cat > tmp/nmp-intake-auth.yaml <<'YAML'
platform:
  runtime: "docker"
  base_url: "http://127.0.0.1:8080"

auth:
  enabled: true
  policy_decision_point_provider: embedded
  policy_decision_point_base_url: "http://127.0.0.1:8080"
  policy_data_refresh_interval: 1
  bundle_cache_seconds: 0
  admin_email: "admin@example.com"

entities: {}
intake: {}
YAML
```

Run the same local service set with that config:

```bash
uv run nemo services run \
  --services auth,entities,intake \
  --config tmp/nmp-intake-auth.yaml \
  --host 127.0.0.1 \
  --port 8080
```

Seed a workspace and role bindings with a service principal:

```bash
BASE=http://127.0.0.1:8080
SERVICE='X-NMP-Principal-Id: service:local-test'

curl -i -X POST "$BASE/apis/entities/v2/workspaces" \
  -H "$SERVICE" \
  -H 'Content-Type: application/json' \
  -d '{"name":"default"}'

curl -i -X POST "$BASE/apis/auth/v2/iam/role-bindings?wait_role_propagation=false" \
  -H "$SERVICE" \
  -H 'Content-Type: application/json' \
  -d '{"principal":"viewer@test.com","workspace":"default","role":"Viewer"}'

curl -i -X POST "$BASE/apis/auth/v2/iam/role-bindings?wait_role_propagation=false" \
  -H "$SERVICE" \
  -H 'Content-Type: application/json' \
  -d '{"principal":"editor@test.com","workspace":"default","role":"Editor"}'
```

Expected permission checks:

```bash
# Viewer can read Intake data in the workspace.
curl -i "$BASE/apis/intake/v2/workspaces/default/entries" \
  -H 'X-NMP-Principal-Id: viewer@test.com'

# Viewer cannot create Intake data.
curl -i -X POST "$BASE/apis/intake/v2/workspaces/default/entries" \
  -H 'X-NMP-Principal-Id: viewer@test.com' \
  -H 'Content-Type: application/json' \
  -d '{"data":{"request":{"messages":[]},"response":{"choices":[]}},"context":{"app":"default/test-app","task":"chat"}}'

# Editor can create Intake data.
curl -i -X POST "$BASE/apis/intake/v2/workspaces/default/entries" \
  -H 'X-NMP-Principal-Id: editor@test.com' \
  -H 'Content-Type: application/json' \
  -d '{"data":{"request":{"messages":[]},"response":{"choices":[]}},"context":{"app":"default/test-app","task":"chat"}}'

# The path workspace is authoritative over query filters.
curl --globoff -i "$BASE/apis/intake/v2/workspaces/default/entries?filter[workspace]=other" \
  -H 'X-NMP-Principal-Id: viewer@test.com'
```

The Studio Intake UI remains disabled by default in
`web/packages/studio/src/constants/environment.ts`. When UI exposure is ready,
wire `INTAKE_ENABLED` back to `featureFlags.intakeEnabled` and use
`VITE_FF_INTAKE_ENABLED=true` with `VITE_INTAKE_MICROSERVICE_URL` pointing at
the local platform runner.

### Studio and Azure Scopes

The shared Azure app registration currently exposes the broad platform scopes,
not the Intake-specific scopes. Keep local Studio auth scopes at:

```bash
VITE_AUTH_SCOPES="platform:read platform:write openid profile email offline_access"
```

Do not add `intake:read` or `intake:write` to local Studio env files or shared
defaults until the Azure app registration for
`api://e9174c91-5abf-4e3c-acd5-8d78bd971a30` exposes those scopes and admin
consent has been granted. If Studio redirects back to `/auth/success` with an
`AADSTS65005` error saying `intake:read` does not exist, remove the Intake
scopes from `web/packages/studio/env/.env.dev.local`, restart the Vite dev
server, and clear browser auth storage before logging in again.

The backend authorization config allows both forms for Intake endpoints:

- `platform:read` or `intake:read` for read/list endpoints
- `platform:write` or `intake:write` for create/update/delete endpoints

### TODOs

- Keep Studio Intake disabled by default until the v2 Intake UI path is ready.
- Before enabling `intake:read` and `intake:write` in Studio defaults, add both
  scopes to the Azure app registration and grant consent.
- After Azure scopes exist, test Studio login with Intake enabled and verify
  Viewer/Editor role behavior against `/apis/intake/v2/workspaces/{workspace}`.

```bash
# Install dependencies (from repo root)
uv sync --dev

# Run tests
cd services/intake
pytest tests/test_api_refactored.py -v

# Start postgres database
docker-compose up -d postgres

# Start service
export POSTGRES_USER=nemo_user
export POSTGRES_PASSWORD=nemo_password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=nemo_db
python src/entrypoint.py
```

## API Documentation

The full API specification is available at `/docs` when the service is running (e.g., http://localhost:8080/docs).

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_api_refactored.py -v
```

Tests cover:

- Apps CRUD operations (6 tests)
- Tasks CRUD operations (5 tests)
- Entries CRUD operations (8 tests)
- Auto-registration of apps/tasks
- longest_per_thread filtering
- Health checks
