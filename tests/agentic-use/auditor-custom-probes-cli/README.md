# Custom Audit with Selected Probes (CLI)

Harbor eval

Tests the agent's ability to create a custom audit configuration with specific
selected probes, create an audit target, run an audit job with the custom config,
and attempt to retrieve results/hit logs.

## Known Limitations

**Audit jobs do not run to completion in the Harbor test environment.**

The audit job execution chain requires:
1. A pre-built `auditor-tasks` Docker image (contains Garak framework)
2. Docker-in-Docker (DOOD) access via `/var/run/docker.sock`
3. A working inference endpoint for Garak probes to call

The Harbor container runs the NeMo Platform API in quickstart mode with the jobs controller
(scheduler + reconciler), but the `auditor-tasks` image is not available and
Docker socket access is not configured. Jobs will stay in `CREATED` or `PENDING`
state.

As a result, the verifier validates:
- **Setup correctness**: config has the right probes, target references the right
  model, job spec wires config + target together
- **Agent behavior**: trajectory analysis confirms the agent attempted to retrieve
  results and hit logs (even though they won't be available)

It does **not** verify:
- That only the selected probes actually ran
- That results contain detailed findings
- That hit logs show specific vulnerabilities
