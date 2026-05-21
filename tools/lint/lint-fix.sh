#!/usr/bin/env bash
set -euo pipefail
# Run all auto-fix commands in dependency order:
#   1. OpenAPI spec regeneration (other steps depend on this)
#   2. Web SDK regeneration (Orval reads openapi/ga/individual/platform.openapi.yaml)
#   3. Stainless sync (pulls updated Python SDK from Stainless; openapi already done in step 1)
#   4. Python style (ruff; run before vendoring so generated files aren't re-linted)
#   5. CLI command generation (the vendoring and docs are handled by the next step)
#   6. Vendor all packages (covers nemo_platform_ext too) + CLI reference docs
#   7. License update (may change after vendoring)
#   8. Config reference docs (independent, but run after structural changes)
#   9. Auth docs (regenerate permissions reference from static-authz.yaml)
#
# Note: update-sdk = build-policy + refresh-openapi + stainless + update-cli, so we use
# stainless directly here to avoid re-running refresh-openapi and update-cli redundantly.
# Note: update-cli = generate-cli-commands + vendor-nemo-platform-ext + generate-cli-reference-docs,
# but vendor-nemo-platform-ext is a subset of make vendor and generate-cli-reference-docs would
# run twice. So we run generate-cli-commands alone, then let make vendor cover all vendoring.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${CI_PROJECT_DIR:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
cd "${PROJECT_ROOT}" || exit 1

declare -a steps=(
  "refresh-openapi:make refresh-openapi"
  "web-sdk:bash tools/lint/lint-fix-web-sdk.sh"
  "stainless:uv run --frozen nemo-platform-sdk-tools is-up-to-date --output-dir \"${TMPDIR:-/tmp}/nmp-sdk-lint\" || make stainless"
  "python-style:uv run ruff format && uv run ruff check --fix"
  "generate-cli-commands:make generate-cli-commands"
  "vendor+cli-reference-docs:make vendor && make generate-cli-reference-docs"
  "update-licenses:bash tools/lint/lint-fix-licenses.sh"
  "auth-config:uv run python services/core/auth/scripts/auth-tools.py update"
  "generate-config-docs:uv run generate-config-docs"
  "generate-auth-docs:uv run python services/core/auth/scripts/auth-tools.py generate-docs"
)

declare -a failed=()
declare -a timing_rows=()
for entry in "${steps[@]}"; do
  name="${entry%%:*}"
  cmd="${entry#*:}"
  echo ">>> ${name}: ${cmd}"
  start=$(date +%s)
  if eval "${cmd}"; then
    echo "[DONE] ${name}"
    result="DONE"
  else
    echo "[FAIL] ${name}"
    failed+=("${name}")
    result="FAIL"
  fi
  elapsed=$(( $(date +%s) - start ))
  timing_rows+=("$(printf '%-40s %s' "${name}" "${result} ${elapsed}s")")
  echo ""
done

echo "--- Fix summary ---"
echo "Completed: $((${#steps[@]} - ${#failed[@]}))"
echo "Failed: ${#failed[@]}"
echo ""
echo "Timings:"
for row in "${timing_rows[@]}"; do
  printf '  %s\n' "${row}"
done
if [[ ${#failed[@]} -gt 0 ]]; then
  echo ""
  echo "Failed steps: ${failed[*]}"
  exit 1
fi
exit 0
