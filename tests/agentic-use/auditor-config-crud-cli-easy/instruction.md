# Auditor Config CRUD Operations (CLI)

You have access to the `nemo` CLI for NeMo Platform operations. Note: MCP tools are not available in this environment - you must use the CLI.

## Task

Complete the following auditor configuration CRUD operations using the `nemo` CLI:

1. List the existing global audit configs to understand the available structure (there should be a "default" config)
2. Create an audit config named `harbor-test-config` with description `Test config for harbor eval` that uses the `dan.AutoDANCached` probe
3. Verify the config was created by retrieving it with a get command
4. List all configs in the workspace and confirm `harbor-test-config` appears
5. Update `harbor-test-config` to change its description to `Updated test config`
6. Verify the update was applied by retrieving the config again
7. Delete the config `harbor-test-config`
8. Create a new config named `harbor-final-config` with description `Final config for verification` that uses the `dan.DanInTheWild` probe

## Available CLI Commands

The `nemo` CLI is available at `/app/.venv/bin/nemo`. The CLI connects to the local NeMo Platform API server at http://localhost:8080 by default.

### Audit Config Commands

- `nemo audit configs list-global` - List built-in global audit configs (use to see the expected JSON structure)
- `nemo audit configs list` - List all audit configs in the workspace
- `nemo audit configs create <name> --description "<description>" --plugins '<json>' --reporting '<json>' --run '<json>' --system '<json>'` - Create a config
- `nemo audit configs get <name>` - Retrieve a config by name
- `nemo audit configs update <name> --description "<description>"` - Update a config (pass only the fields you want to change)
- `nemo audit configs delete <name>` - Delete a config

### Config JSON Structure

Audit configs require JSON for `plugins`, `reporting`, `run`, and `system` fields. A minimal example:

- **plugins**: `{"probe_spec": "dan.AutoDANCached"}` — the `probe_spec` string specifies which probes to run
- **reporting**: `{}`
- **run**: `{}`
- **system**: `{"lite": true}`

**Tip:** Run `nemo audit configs list-global` and inspect the built-in `default` config to see the full expected structure.

## Success Criteria

The task is complete when:
- The config `harbor-test-config` was created, updated, and then deleted
- A config named `harbor-final-config` exists with description `Final config for verification`
- The `harbor-final-config` uses the `dan.DanInTheWild` probe
- The config `harbor-test-config` no longer exists (was deleted)
