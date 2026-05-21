---
name: nemo-spec
description: Captures a NeMo Platform agent spec as a durable artifact at agents/<name>.spec.md. Reads the template, writes the file, shows it to the user for sign-off, then hands off to nemo-build-agent. Use over generic planning skills for any NeMo Platform agent spec.
triggers:
  - write the spec
  - save the design
  - capture what we agreed
  - persist the agent design
  - nemo spec
  - write agent spec
not-for:
  - nemo-explore (use to gather the design before writing the spec)
  - nemo-build-agent (use to scaffold and deploy once the spec is signed off)
  - nemo-skill-selection (use for dispatch when intent is unclear)
compatibility: nemo-platform >= 0.1.0; writes one markdown file under agents/; no network; safe under any sandbox; idempotent if user confirms overwrite.
maturity: active
license: Apache-2.0
user-invocable: true
allowed-tools: [Read, Write, Edit, Bash]
---

# NeMo Platform agent spec

Turn the answers from `nemo-explore` into a durable artifact. The spec is the contract `nemo-build-agent` reads to scaffold the NAT workflow YAML. Without it, the build skill has to re-ask everything.

## Pre-flight

Check whether the spec already exists. If so, ask the user whether to overwrite or pick a different name.

```bash
ls "agents/${NAME}.spec.md" 2>/dev/null && echo "spec_exists" || echo "spec_new"
```

## What you do

1. **Confirm the agent name.** Lowercase, hyphens, short: `it-helpdesk`, `support-triage`, `code-reviewer`. If the user has not named it, propose two options based on the job.

2. **Validate the name.** Must match `[a-z][a-z0-9-]*`. Reject and re-ask if not.

3. **Write the file.** Path: `agents/<name>.spec.md`. Create the `agents/` directory if it does not exist. Use the template at `references/templates/agent-spec.md`. Read the template before writing so the structure is right.

4. **Fill every section.** No "TBD" in a saved spec. If a section has nothing, leave a one-line note explaining why ("Prompt-only. No tools beyond clock.").

5. **Show the spec to the user.** After writing, print the full file contents and ask: "Does this match what we agreed? Edit anything you want to change."

6. **Hand off.** Once confirmed, tell the user `nemo-build-agent` will read `agents/<name>.spec.md` and produce the workflow YAML.

## Verification

After writing the file, confirm it exists and is non-empty:

```bash
test -s "agents/${NAME}.spec.md" && echo "spec_written" || echo "spec_missing"
```

Do not announce success until this check passes and the user has confirmed the contents match what they agreed.

## If verification fails

| Symptom | Cause | Recovery |
|---|---|---|
| `spec_missing` after write | Wrong working directory or permission denied | Run `pwd`, check the user is in the cloned repo; check `~/.config/nmp/` write grant from `nemo-setup` |
| User says "this is wrong" | Spec captured the wrong answers | Edit the relevant section in place; do not rewrite the whole file |
| Name validation keeps failing | User keeps proposing names with underscores or capitals | Pin the regex `[a-z][a-z0-9-]*` and show one example that passes |
| `nemo-explore` was skipped | User invoked `nemo-spec` cold | Route back to `nemo-explore` and return here when the conversation is done |

## What this skill is not

This skill does not produce NAT workflow YAML. The spec is the human-readable design; the YAML is generated downstream by `nemo-build-agent`. Once the agent is deployed, edits go through a re-spec + re-build, not file surgery on the YAML.

## Gotchas

- **The template is the source of truth for structure.** Do not improvise sections. Read `references/templates/agent-spec.md` and follow it.
- **Spec lives next to the workflow YAML.** Both files end up in `agents/`. Keep them adjacent so a future read of the directory shows design and implementation together.
- **Names with underscores or capitals break tools.** Validate against `[a-z][a-z0-9-]*`. Reject and re-ask if not.
- **Do not write the spec until `nemo-explore` has been run.** If the user invokes this skill cold, route them back to `nemo-explore` first.
