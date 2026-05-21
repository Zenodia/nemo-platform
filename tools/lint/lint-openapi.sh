#!/usr/bin/env bash
set -euo pipefail
# Verify OpenAPI specs are up to date by regenerating and diffing.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${CI_PROJECT_DIR:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
cd "${PROJECT_ROOT}"

mkdir -p openapicheck
cp openapi/openapi.yaml openapicheck/openapi.yaml
cp openapi/ga/openapi.yaml openapicheck/openapi.ga.yaml
script/generate-openapi-spec.sh
diff openapi/openapi.yaml openapicheck/openapi.yaml
diff openapi/ga/openapi.yaml openapicheck/openapi.ga.yaml
