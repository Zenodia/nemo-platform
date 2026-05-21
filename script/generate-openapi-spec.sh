#!/usr/bin/env bash
uv run --frozen python -m script.generate_openapi_spec -v "$@"
