#!/usr/bin/env sh
# Builds policy.wasm from OPA Rego policy sources using a pinned OPA version.
#
# Used in all contexts: local dev, SDK wheel builds, and Docker image builds.
# The pinned version ensures reproducible output regardless of what (if anything)
# the developer has installed locally.
#
# Environment variables:
#   OUTPUT_DIR   - Directory to write policy.wasm into.
#                  Default: services/core/auth/src/nmp/core/auth/assets
#   REPO_ROOT    - Repository root. Default: auto-detected via git.
set -eu

# --- Configuration ---
REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel)}"

POLICY_DIR="${REPO_ROOT}/services/core/auth/src/nmp/core/auth/app/policies"
OUTPUT_DIR="${OUTPUT_DIR:-${REPO_ROOT}/services/core/auth/src/nmp/core/auth/assets}"
ENTRYPOINTS="-e authz/allow -e authz/has_permissions -e authz/has_role"

if ! command -v opa > /dev/null; then
  echo "opa command not found. exiting.."
  exit 1
fi

echo "###############################"
opa version
echo "###############################"
echo ""

# --- Build policy.wasm ---
echo "Building policy.wasm from ${POLICY_DIR}..."
BUNDLE_TMP="$(mktemp -d)"
echo "Bundle temp dir: ${BUNDLE_TMP}"

cleanup() { rm -rf "${BUNDLE_TMP}"; }
trap cleanup EXIT

# Build in a subshell so the cd doesn't affect OUTPUT_DIR resolution.
# Using relative paths (*.rego) ensures the wasm output is path-independent.
# shellcheck disable=SC2086

(cd "${POLICY_DIR}" && opa build -t wasm ${ENTRYPOINTS} -o "${BUNDLE_TMP}/bundle.tar.gz" *.rego)

ls -1 "${BUNDLE_TMP}"

# --- Extract WASM ---
mkdir -p "${OUTPUT_DIR}"
tar -C "${OUTPUT_DIR}" -zxvf "${BUNDLE_TMP}/bundle.tar.gz" "/policy.wasm"
echo "policy.wasm written to ${OUTPUT_DIR}/policy.wasm"

ls -lh "${OUTPUT_DIR}/policy.wasm"
