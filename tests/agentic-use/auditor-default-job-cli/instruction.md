# Run Default Audit Job (CLI)

You have access to the `nmp` CLI for NeMo Platform operations. Note: MCP tools are not available in this environment - you must use the CLI.

The `nmp` CLI is available at `/app/.venv/bin/nmp`. The CLI connects to the local NeMo Platform API server at http://localhost:8080 by default. CLI auth is pre-configured.

## Context

An inference provider named `nvidia-inference` has been pre-configured in this environment with model access via NVIDIA's inference API. You can use this provider when creating audit targets.

## Task

Using the `nmp` CLI, create an audit target, create an audit config, and run an audit job:

1. **Create an audit target** named `audit-target` that references model `aws/anthropic/bedrock-claude-sonnet-4-5-v1` through the `nvidia-inference` provider
2. **Create an audit config** named `default` with appropriate settings
3. **Create an audit job** named `default-audit-job` using the `default` config and the `audit-target` target
4. **Check the job status** to see its current state

Note: The audit job may take a long time to complete or may remain in a pending/created state in this environment. That is expected. The important thing is that the job is created correctly.

## Success Criteria

The task is complete when:
- An audit target named `audit-target` exists referencing the model through the provider
- An audit config named `default` exists
- An audit job named `default-audit-job` has been created with the default config
- The job status has been checked at least once
