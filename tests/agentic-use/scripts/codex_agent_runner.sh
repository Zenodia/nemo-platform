#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail
model_args=()
if [ -n "${AGENT_MODEL:-}" ]; then
  model_args=(--model "${AGENT_MODEL}")
fi
export CODEX_HOME="${CODEX_HOME:-/home/harbor/.codex}"
if [ -f /tmp/codex_host_auth.json ]; then
  mkdir -p "$CODEX_HOME"
  cp /tmp/codex_host_auth.json "$CODEX_HOME/auth.json"
fi
python - <<'PY'
from pathlib import Path

Path("/tmp/codex_output_schema.json").write_text(@@CODEX_STRUCTURED_OUTPUT_SCHEMA@@, encoding="utf-8")
instruction = Path(@@INSTRUCTION_CONTAINER@@).read_text(encoding="utf-8")
prompt = @@CODEX_STRUCTURED_PROMPT_PREFIX@@ + "\n\nTask instruction:\n" + instruction
Path("/tmp/codex_structured_prompt.md").write_text(prompt, encoding="utf-8")
PY
set +e
codex exec \
  --skip-git-repo-check \
  --sandbox read-only \
  --cd /app \
  --output-schema /tmp/codex_output_schema.json \
  --output-last-message /logs/agent/codex_structured_output.json \
  --json \
  "${model_args[@]}" \
  - < /tmp/codex_structured_prompt.md \
  > /tmp/nat_agent.log 2> /tmp/nat_agent.stderr
rc=$?
set -e
cp /tmp/nat_agent.log /logs/agent/nat_agent.log 2>/dev/null || true
cp /tmp/nat_agent.stderr /logs/agent/nat_agent.stderr 2>/dev/null || true
if [ $rc -eq 0 ]; then
  python - <<'PY'
import json
import sys
from pathlib import Path, PurePosixPath

app_root = Path("/app")
payload_path = Path("/logs/agent/codex_structured_output.json")
try:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"Failed to parse Codex structured output: {exc}", file=sys.stderr)
    sys.exit(1)

final_summary = payload.get("final_summary")
if not isinstance(final_summary, str) or not final_summary.strip():
    print("Codex structured output missing non-empty final_summary", file=sys.stderr)
    sys.exit(1)

output_files = payload.get("output_files")
if not isinstance(output_files, list):
    print("Codex structured output missing output_files list", file=sys.stderr)
    sys.exit(1)

for index, entry in enumerate(output_files):
    if not isinstance(entry, dict):
        print(f"output_files[{index}] must be an object", file=sys.stderr)
        sys.exit(1)
    rel = entry.get("path")
    content = entry.get("content")
    if not isinstance(rel, str) or not rel.strip():
        print(f"output_files[{index}].path must be a non-empty string", file=sys.stderr)
        sys.exit(1)
    if not isinstance(content, str):
        print(f"output_files[{index}].content must be a string", file=sys.stderr)
        sys.exit(1)

    rel_path = PurePosixPath(rel)
    if rel_path.is_absolute() or not rel_path.parts:
        print(f"output_files[{index}].path must be relative to /app: {rel}", file=sys.stderr)
        sys.exit(1)
    if any(part in {"", ".", ".."} for part in rel_path.parts):
        print(f"output_files[{index}].path contains an unsafe path segment: {rel}", file=sys.stderr)
        sys.exit(1)
    if rel_path.parts[0] == ".git":
        print(f"output_files[{index}].path may not target .git: {rel}", file=sys.stderr)
        sys.exit(1)

    target = app_root.joinpath(*rel_path.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

Path("/logs/agent/final_message.txt").write_text(final_summary.strip() + "\n", encoding="utf-8")
PY
  rc=$?
fi
exit $rc
