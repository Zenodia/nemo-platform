---
name: auditor
description: >
  NeMo auditor CLI reference for audit configs, targets, and jobs.
  Use when the task involves audit configurations, audit targets, audit jobs,
  vulnerability scanning, probes, or `nemo audit` CLI commands.
---

# NeMo Auditor CLI Reference

## Environment

- **API server**: `http://localhost:8080` (default)
- **Default workspace/namespace**: `default`

## Audit Config Commands

```bash
# List configs across all accessible workspaces (omit --workspace for the cross-workspace set, including built-in globals)
nemo audit configs list

# List workspace configs
nemo audit configs list --workspace <ws>

# Create a config (all four section flags required)
nemo audit configs create <name> \
  --description "<description>" \
  --plugins '<json>' \
  --reporting '<json>' \
  --run '<json>' \
  --system '<json>'

# Get a config
nemo audit configs get <name>

# Update a config (pass only fields to change)
nemo audit configs update <name> --description "<new description>"

# Delete a config
nemo audit configs delete <name>
```

### Config JSON Structure

Minimal example for each required field:
- **plugins**: `{"probe_spec": "dan.AutoDANCached"}` — specifies which probes to run
- **reporting**: `{}`
- **run**: `{}` or `{"generations": 5}`
- **system**: `{"lite": true}`

Common probe specs: `dan.AutoDANCached`, `dan.DanInTheWild`, `dan.goodside`

## Audit Target Commands

```bash
# Create a target
nemo audit targets create <name> \
  --model <model-name> \
  --type <type> \
  --description "<description>"

# Create a target with a provider (for real inference endpoints)
nemo audit targets create <name> \
  --model <model-name> \
  --type <type> \
  --options '{"provider": "<provider-name>"}'

# List targets
nemo audit targets list

# Get a target
nemo audit targets get <name>

# Update a target
nemo audit targets update <name> --description "<new description>"

# Delete a target
nemo audit targets delete <name>
```

Target types: `nim`, `openai`

## Audit Job Commands

```bash
# Create a job (spec references config and target as namespace/name)
nemo audit jobs create <job-name> \
  --spec '{"config": "default/<config-name>", "target": "default/<target-name>"}'

# Check job status
nemo audit jobs get-status <job-name>

# List jobs
nemo audit jobs list
```

Jobs may take a long time or remain in pending/created status. That is expected.

## Typical Workflows

### Config CRUD

1. `nemo audit configs list` (no `--workspace`) — inspect built-in/global configs across all accessible workspaces
2. `nemo audit configs create my-config ...` — create
3. `nemo audit configs get my-config` — verify
4. `nemo audit configs update my-config --description "..."` — update
5. `nemo audit configs delete my-config` — delete

### Run an Audit Job

1. Create a target pointing to the model endpoint
2. Create a config with probe selection
3. Create a job referencing `default/<config>` and `default/<target>`
4. Check status with `nemo audit jobs get-status`
