#!/usr/bin/env bash
set -euo pipefail
uv run pre-commit run check-merge-conflict
