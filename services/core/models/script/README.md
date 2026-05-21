# v2_deployment_migration.py — Migration Guide

Migrates V1 NeMo Platform model deployments (deployment configs, model deployments, and
model entities) to V2 NeMo Platform.

## Prerequisites

- Python 3.11+, [uv](https://docs.astral.sh/uv/) installed
- V1 NeMo Platform instance accessible from your machine
- V2 NeMo Platform instance accessible from your machine
- (Optional) Run the **files migration** (`services/core/files/script/v2_migration.py`)
  before `apply` so that model artifact filesets exist in V2 and are linked automatically.
  The models plan emits `files_repos_needed` to tell you exactly which repos to migrate.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `NMP_V1_BASE_URL` | **Yes** | Base URL of the V1 NeMo Platform instance. Alias: `NMP_BASE_URL`. Can also be passed via `--v1-base-url`. |
| `NMP_V1_API_KEY` | No | API key for the V1 instance. Can also be passed via `--v1-api-key`. |
| `NMP_V2_BASE_URL` | No* | Base URL of the V2 NeMo Platform instance. Alias: `NEMO_MICROSERVICES_BASE_URL`. Can also be passed via `--v2-base-url`. *If omitted, the script reads the URL from the `nemo auth login` context. |

```bash
export NMP_V1_BASE_URL=https://v1.example.com
export NMP_V2_BASE_URL=https://v2.example.com
```

## Full Migration Sequence

### Step 1 — Generate a models plan

The plan discovers all V1 namespaces, deployment configs, deployments, and model entities.
It also produces a `files_repos_needed` list so you know which datastore repos to migrate.

```bash
cd services/core/models/script

# Single namespace
uv run v2_deployment_migration.py plan \
  --namespace <namespace> \
  --plan plan.json

# Namespace prefix (all matching namespaces)
uv run v2_deployment_migration.py plan \
  --namespace-prefix my-org- \
  --plan plan.json
```

### Step 2 — (Optional) Migrate artifact filesets

If any model entities reference artifact filesets, migrate them now using the repo list from
the plan. This must complete before `apply` so the script can link filesets to model entities.

```bash
cd services/core/files/script

# Build --repo-id args from the models plan
REPO_ARGS=$(jq -r '.files_repos_needed[] | "--repo-id \(.)"' ../models/script/plan.json | tr '\n' ' ')

# Skip this block if REPO_ARGS is empty (no artifact filesets to migrate)
uv run v2_migration.py plan $REPO_ARGS --output files_plan.json
uv run v2_migration.py apply --plan files_plan.json
```

Review the plan before proceeding:
- `plan.json` contains `files_repos_needed`, `model_entities`, `configs`, `deployments`, and their `skipped_*` counterparts.
- Each entry includes a `warnings` list for non-fatal field-mapping issues.
- Check `summary` for counts.

### Step 3 — Validate connectivity

```bash
cd services/core/models/script
uv run v2_deployment_migration.py setup \
  --check \
  --namespace <namespace>
```

Expected output:
```
V1 deployment service: OK
V2 inference service: OK
```

### Step 4 — Apply the plan

```bash
# Dry run (no V2 writes)
uv run v2_deployment_migration.py apply \
  --plan plan.json \
  --dry-run

# Real apply
uv run v2_deployment_migration.py apply \
  --plan plan.json \
  --result-output result.json
```

To merge all namespaces into a single V2 workspace (names are prefixed to avoid collisions):

```bash
uv run v2_deployment_migration.py apply \
  --plan plan.json \
  --target-workspace merged-workspace \
  --result-output result.json
```

### Step 5 — Verify

Send a "hello world" chat-completion request to each migrated deployment to confirm reachability:

```bash
uv run v2_deployment_migration.py verify --plan plan.json
```

Adjust the per-model timeout (default 60 s):

```bash
uv run v2_deployment_migration.py verify --plan plan.json --timeout 120
```

## What Is Migrated

| Object | Migrated | Notes |
|---|---|---|
| Model entities | Yes | Name, description, spec, base_model, finetuning_type, api_endpoint, custom_fields, model_providers, ownership, project, prompt |
| Model entity fileset | Yes (conditional) | Linked automatically if the files migration has already been run |
| Deployment configs (NIM) | Yes | gpu, image_name, image_tag, additional_envs, pvc_size→disk_size, disable_lora_support→lora_enabled (inverted) |
| Model deployments (READY) | Yes | |

## What Is Skipped / Dropped

| Object / Field | Behavior |
|---|---|
| External-endpoint-only configs | Skipped — register via inference gateway instead |
| Non-READY deployments | Skipped — only `READY` deployments are migrated |
| LoRA / p-tuning adapter configs | Warning emitted; adapter migration is a separate step |
| `DeploymentConfig.external_endpoint` (when NIM config also present) | Warning emitted, field dropped |
| `NIMDeploymentConfig.namespace` (k8s namespace) | Warning emitted, field dropped — use `k8s_nim_operator_config` in V2 |
| `ModelDeployment.async_enabled` | Warning emitted, field dropped — no V2 equivalent |
| Model artifact filesets | Warning emitted if fileset not found in V2; model entity is still created |

---

# v2_deployment_migration.py — Test Cases

## Test Cases

### TC-01: setup — connectivity check passes

Verifies both services are reachable and credentials resolve.

```bash
uv run v2_deployment_migration.py setup \
  --v1-base-url http://localhost:8080 \
  --v2-base-url http://localhost:8002 \
  --check --namespace test-ns
```

**Expected:** Prints `V1 deployment service: OK` and `V2 inference service: OK`. Exit 0.

---

### TC-02: setup — missing V1 URL fails clearly

```bash
uv run v2_deployment_migration.py setup --v2-base-url http://localhost:8002 --check
```

**Expected:** Error message referencing `--v1-base-url` or `NMP_V1_BASE_URL`. Non-zero exit.

---

### TC-03: plan — basic NIM deployment translates correctly

```bash
uv run v2_deployment_migration.py plan \
  --v1-base-url http://localhost:8080 \
  --v2-base-url http://localhost:8002 \
  --namespace test-ns \
  --plan plan.json
```

**Expected in `plan.json`:**
- `configs` contains an entry for `nim-config-basic` with:
  - `v2_workspace: "test-ns"`, `v2_config_name: "nim-config-basic"`
  - `nim_deployment.gpu: 1`, `nim_deployment.image_name: "nvcr.io/..."`, `nim_deployment.image_tag: "1.3.0"`
  - `model_entity_id: "test-ns/llama-3.1-8b"`
  - `skipped: false`, `warnings: []`
- `deployments` contains `dep-basic` mapped to workspace `test-ns`, config `nim-config-basic`.

---

### TC-04: plan — `disable_lora_support` is inverted to `lora_enabled`

Inspect `plan.json` from TC-03.

**Expected:** Config `nim-config-lora-disabled` has `nim_deployment.lora_enabled: false`
(inverted from V1 `disable_lora_support: true`). Also `nim_deployment.disk_size: "100Gi"` (renamed from `pvc_size`).

---

### TC-05: plan — k8s namespace generates a warning and is dropped

Inspect `plan.json` from TC-03.

**Expected:** Config `nim-config-with-k8s-ns` has `warnings` containing a message about
`NIMDeploymentConfig.namespace` being dropped. The `nim_deployment` dict does not contain a
`namespace` key.

---

### TC-06: plan — external-endpoint-only config is skipped

Inspect `plan.json` from TC-03.

**Expected:**
- `skipped_configs` contains `ext-config-only` with `skip_reason` mentioning `external_endpoint`.
- `skipped_deployments` contains `dep-ext-only` with a reason referencing the skipped config.
- `summary.skipped_config_count >= 1`, `summary.skipped_deployment_count >= 1`.

---

### TC-07: plan — config with both NIM and external endpoint warns but does not skip

Inspect `plan.json` from TC-03.

**Expected:** Config `nim-config-with-ext` is in `configs` (not skipped), with a `warnings` entry
about the `external_endpoint` being dropped and pointing to inference gateway.

---

### TC-08: plan — `async_enabled` deployment generates a warning

Inspect `plan.json` from TC-03.

**Expected:** Deployment `dep-async` is present in `deployments` with a `warnings` entry
mentioning `async_enabled` was dropped.

---

### TC-09: plan — non-READY deployments are excluded

Set `dep-basic` to `PENDING` in V1 DB, regenerate the plan.

```sql
UPDATE model_deployments SET status = 'PENDING' WHERE name = 'dep-basic' AND namespace = 'test-ns';
```
```bash
uv run v2_deployment_migration.py plan ... --output plan-pending.json
```

**Expected:** `dep-basic` does not appear in `plan-pending.json` `deployments`. `summary.skipped_deployment_count` is higher than in TC-03.

---

### TC-10: plan — namespace-prefix scoping

```bash
uv run v2_deployment_migration.py plan \
  --v1-base-url http://localhost:8080 \
  --v2-base-url http://localhost:8002 \
  --namespace-prefix test- \
  --output plan-prefix.json
```

**Expected:** Only deployments/configs from `test-ns` appear. `other-ns` is excluded.

---

### TC-11: plan — multiple explicit namespaces

```bash
uv run v2_deployment_migration.py plan \
  --v1-base-url http://localhost:8080 \
  --v2-base-url http://localhost:8002 \
  --namespace test-ns \
  --namespace other-ns \
  --output plan-multi.json
```

**Expected:** Deployments from both `test-ns` and `other-ns` appear in `plan-multi.json`.

---

### TC-12: apply — dry run makes no V2 changes

```bash
uv run v2_deployment_migration.py apply \
  --v1-base-url http://localhost:8080 \
  --v2-base-url http://localhost:8002 \
  --plan plan.json \
  --dry-run \
  --result-output result-dry.json
```

**Expected:**
- `result-dry.json` shows `dry_run: true` and all `deployment_status: "dry_run"`.
- No workspaces, configs, or deployments created in V2 (verify via `GET /apis/models/v2/workspaces/test-ns/deployments`).

---

### TC-13: apply — creates workspace, configs, and deployments in V2

```bash
uv run v2_deployment_migration.py apply \
  --v1-base-url http://localhost:8080 \
  --v2-base-url http://localhost:8002 \
  --plan plan.json \
  --result-output result.json
```

**Expected:**
- `result.json` shows `summary.created_deployments > 0`, `summary.failed_deployments: 0`.
- Workspace `test-ns` exists in V2.
- Config `nim-config-basic` exists in workspace `test-ns` with correct `nim_deployment` fields.
- Deployment `dep-basic` exists in workspace `test-ns` referencing config `nim-config-basic`.
- Skipped deployments (ext-only) do not appear in V2.

Verify:
```python
from nemo_platform import NeMoPlatform
client = NeMoPlatform(base_url="http://localhost:8002")

config = client.inference.deployment_configs.retrieve("nim-config-basic", workspace="test-ns")
assert config.nim_deployment.gpu == 1
assert config.nim_deployment.image_tag == "1.3.0"

dep = client.inference.deployments.retrieve("dep-basic", workspace="test-ns")
assert dep.config == "nim-config-basic"
```

---

### TC-14: apply — idempotent (safe to run twice)

Run the apply command from TC-13 a second time.

**Expected:**
- `result.json` shows `summary.created_deployments: 0`, `summary.failed_deployments: 0`.
- All `deployment_status` values are `"exists"`.

---

### TC-15: apply — `--target-workspace` merges namespaces with name prefixing

```bash
uv run v2_deployment_migration.py apply \
  --v1-base-url http://localhost:8080 \
  --v2-base-url http://localhost:8002 \
  --plan plan-multi.json \
  --target-workspace merged-ws \
  --result-output result-merged.json
```

**Expected:**
- All deployments land in workspace `merged-ws`.
- Config from `test-ns` is named `test-ns-nim-config-basic`.
- Config from `other-ns` is named `other-ns-nim-config-other`.
- Deployment from `test-ns` is named `test-ns-dep-basic`.
- No name collision errors.

---

### TC-16: apply — `--max-deployments` limits scope

```bash
uv run v2_deployment_migration.py apply \
  --v1-base-url http://localhost:8080 \
  --v2-base-url http://localhost:8002 \
  --plan plan.json \
  --max-deployments 1 \
  --result-output result-limited.json
```

**Expected:** `result-limited.json` shows exactly 1 deployment processed.

---

### TC-17: apply — plan with missing config reference is handled gracefully

Manually edit `plan.json` to remove a config entry that a deployment references, then apply.

**Expected:** The affected deployment shows `deployment_status: "skipped: config failed (missing_from_plan)"`. Other deployments complete normally. Exit non-zero.

---

### TC-18: plan requires scope — no namespace args fails

```bash
uv run v2_deployment_migration.py plan \
  --v1-base-url http://localhost:8080 \
  --v2-base-url http://localhost:8002 \
  --plan plan.json
```

**Expected:** Error message requiring `--namespace` or `--namespace-prefix`. Non-zero exit.
