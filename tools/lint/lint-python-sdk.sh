#!/usr/bin/env bash
set -euo pipefail
# Verify Python SDK is up to date with OpenAPI spec.
OUTPUT_DIR="${CI_PROJECT_DIR:-$(pwd)}/python-sdk-lint"
uv run --frozen nemo-platform-sdk-tools is-up-to-date --output-dir "${OUTPUT_DIR}"
