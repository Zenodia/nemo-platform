# Documentation Scripts

This directory contains helper scripts used by the active MkDocs documentation
workflow. Prefer calling these through `docs/Makefile` unless you are debugging a
script directly.

## Active Scripts

### `setup_mkdocs_env.sh`

Creates or updates the docs-local `.venv-mkdocs` virtual environment with `uv`
and installs `docs/requirements-mkdocs.txt`.

```bash
make -C docs env
```

### `format_code_blocks.py`

Formats supported fenced code blocks in Markdown files. JSON blocks are parsed
and reserialized with stable indentation. Python blocks are formatted with Ruff
from the MkDocs virtual environment.

```bash
make -C docs check-code-blocks
make -C docs format-code-blocks
```

### `lint_notebooks.py`

Lints selected Markdown notebook sources and performs type checks for supported
Python code blocks.

```bash
make -C docs lint-python
```

### `run_notebooks.py`

Runs docs notebooks or Markdown notebook sources that use the `@nemo-nb`
markers. This is a direct utility rather than a Makefile target.

```bash
uv run python docs/_scripts/run_notebooks.py docs/
```

## Tests

The `test_*.py` files validate the active docs helper scripts and can be run
with `uv run pytest` from the repository root.

## Adding Scripts

When adding a script:

1. Put it in `docs/_scripts/`.
2. Wire it into `docs/Makefile` if it is part of the normal docs workflow.
3. Add or update focused tests when the behavior is nontrivial.
4. Document the Make target or direct command in this README.
