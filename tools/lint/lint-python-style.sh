#!/usr/bin/env bash
set -euo pipefail
# Check Python style with ruff (lint and format).
# Uses the ruff version pinned in pyproject.toml dev dependencies.
uv run ruff check
uv run ruff format --check
