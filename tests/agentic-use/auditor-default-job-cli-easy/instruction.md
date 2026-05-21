# Run Default Audit Job (CLI)

You have access to the `nemo` CLI for NeMo Platform operations. Note: MCP tools are not available in this environment - you must use the CLI.

The `nemo` CLI is available at `/app/.venv/bin/nemo`. The CLI connects to the local NeMo Platform API server at http://localhost:8080 by default. CLI auth is pre-configured.

## Context

An inference provider named `nvidia-inference` has been pre-configured in this environment with model access via NVIDIA's inference API. You can use this provider when creating audit targets.

## Task

Using the `nemo` CLI, create an audit target, create an audit config, and run an audit job:

1. Create an audit target named `audit-target` pointing to model `aws/anthropic/bedrock-claude-sonnet-4-5-v1` through the `nvidia-inference` provider
2. Create an audit config named `default`
3. Create an audit job named `default-audit-job` using the `default` config and the `audit-target` target
4. Check the job status

Note: The audit job may take a long time to complete or may remain in a pending/created state. That is expected.

## Available CLI Commands

### Audit Targets

```bash
# Create an audit target (provider is passed via --options as JSON)
nemo audit targets create <name> --model <model-name> --type <type> --options '{"provider": "<provider-name>"}'
```

### Audit Configs

```bash
# Create an audit config (all four section flags are required)
nemo audit configs create <name> --system '<json>' --run '<json>' --plugins '<json>' --reporting '<json>'
```

### Audit Jobs

```bash
# Create an audit job (spec references config and target as namespace/name)
nemo audit jobs create <job-name> --spec '{"config": "<namespace>/<config-name>", "target": "<namespace>/<target-name>"}'

# Check job status
nemo audit jobs get-status <job-name>
```

## Hints

- The provider type for `nvidia-inference` is `openai` (it's an OpenAI-compatible API)
- For the audit config, use minimal valid JSON for each section, e.g.: `--system '{"lite": true}' --run '{"generations": 5}' --plugins '{"probe_spec": "dan,goodside"}' --reporting '{"extended_detectors": false}'`
- Configs and targets you create are in the `default` namespace, so reference them as `default/default` and `default/audit-target`
- Use `--spec` with a JSON string for job creation, not separate flags

## Success Criteria

The task is complete when:
- An audit target named `audit-target` exists referencing the model through the provider
- An audit job named `default-audit-job` has been created with the default config
- The job status has been checked at least once
