#!/usr/bin/env bash
set -euo pipefail
# Verify third-party licenses are up to date.
make check-licenses
# This only runs if the diff doesn't exit early
git restore third_party
