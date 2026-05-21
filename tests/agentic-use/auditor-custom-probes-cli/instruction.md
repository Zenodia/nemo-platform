# Custom Audit with Selected Probes (CLI)

You have access to the `nmp` CLI for NeMo Platform operations. Note: MCP tools are not available in this environment - you must use the CLI.

The `nmp` CLI is available at `/app/.venv/bin/nmp`. The CLI connects to the local NeMo Platform API server at http://localhost:8080 by default. CLI auth is pre-configured.

## Context

An inference provider named `nvidia-inference` has been pre-configured in this environment with model access via NVIDIA's inference API. You can use this provider when creating audit targets.

## Task

Using the `nmp` CLI, create a custom audit configuration with specific selected probes, create an audit target, run an audit job with that custom config, and check the results:

1. **Explore available global audit configs** to understand the config structure and available options
2. **Create an audit target** named `custom-audit-target` that references model `aws/anthropic/bedrock-claude-sonnet-4-5-v1` through the `nvidia-inference` provider
3. **Create a custom audit config** named `custom-probes-config` with description `Custom config with selected probes` that uses exactly these three probes: `dan.DanInTheWild`, `dan.AutoDANCached`, and `dan.Ablation_Dan_11_0`
4. **Verify the config** by retrieving it and confirming the probe selection
5. **Create an audit job** named `custom-probes-job` using the `custom-probes-config` config and the `custom-audit-target` target
6. **Check the job status** to see its current state
7. **Attempt to retrieve the job results** to see detailed findings
8. **Attempt to retrieve hit logs** from the audit job to review any specific vulnerabilities found

Note: The audit job may take a long time to complete or may remain in a pending/created state in this environment. That is expected. Results and hit logs may not be available if the job hasn't completed. The important thing is that the job is created correctly with the custom config, and that you attempt to retrieve results and logs.

## Success Criteria

The task is complete when:
- An audit target named `custom-audit-target` exists referencing the model through the provider
- An audit config named `custom-probes-config` exists with the three specified probes
- An audit job named `custom-probes-job` has been created using the custom config and target
- The job status has been checked at least once
- Results and hit logs retrieval has been attempted
