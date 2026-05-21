#!/usr/bin/env bash
# Sets up the MkDocs virtualenv using uv
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$DOCS_DIR/.venv-mkdocs"
PYTHON_BIN="${PYTHON:-python3}"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating MkDocs virtualenv at $VENV_DIR ..."
    UV_PYTHON_DOWNLOADS=never uv --no-config venv --python "$PYTHON_BIN" "$VENV_DIR"
fi

echo "Installing MkDocs dependencies..."
UV_PYTHON_DOWNLOADS=never uv --no-config pip install --python "$VENV_DIR" -r "$DOCS_DIR/requirements-mkdocs.txt"

echo "✓ MkDocs environment ready: $VENV_DIR"
echo "  Activate with: source $VENV_DIR/bin/activate"
echo "  Or use directly: $VENV_DIR/bin/mkdocs"
