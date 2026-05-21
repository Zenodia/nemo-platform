# Linting Documentation Notebooks

Lint documentation notebooks for syntax and type errors without executing them using `docs/_scripts/lint_notebooks.py`.

## Basic Usage

```sh
uv run python docs/_scripts/lint_notebooks.py <path>
```

Examples:

```sh
# Lint a single notebook
uv run python docs/_scripts/lint_notebooks.py docs/run-inference/tutorials/deploy-llm-nims.md

# Lint all notebooks in a directory
uv run python docs/_scripts/lint_notebooks.py docs/run-inference/
```

### Running in Cursor Agent Sandbox Mode

When running through the Cursor agent in sandbox mode, the agent will set `UV_CACHE_DIR` in the shell environment to avoid read-only filesystem errors. The agent will also use `required_permissions: ["network", "git_write"]` since uv needs network access to download packages and git_write permissions to create cache directories.

## Type Checking

Add `--type-check` to run `ty` type checker on the combined notebook cells:

```sh
uv run python docs/_scripts/lint_notebooks.py docs/run-inference/ --type-check
```

This catches:
- Wrong SDK method names (e.g., `gateway.create()` instead of `gateway.post_model()`)
- Missing attributes (e.g., `client.customizer` when customizer isn't available)
- Type mismatches

Note: `ty` is alpha software and reports some false positives for SDK attributes it can't fully resolve.

## What It Checks

1. **Syntax errors** - Python AST parsing (always enabled)
2. **Type errors** - `ty` type checker (with `--type-check` flag)

## How It Works

The script:
1. Finds notebooks with the `@nemo-nb: process` marker
2. Extracts all Python code cells
3. Combines them into a single file (so cross-cell context works)
4. Runs `ty check` and passes through the output

## Fixing Linter Errors

### ⚠️ NEVER convert Python cells to text blocks

**Changing `\`\`\`python` to `\`\`\`text` is NOT acceptable.** All code must remain executable.

### Acceptable fixes

1. **Fix the actual bug** - Use correct method names, add missing arguments, etc.

2. **Add type ignore comments** for false positives from ty:
   ```python
   response = client.inference.gateway.post_provider(...)
   message = response["choices"][0]["message"]["content"]  # type: ignore[index]
   ```

3. **Add conditional checks** for optional dependencies:
   ```python
   if "API_KEY" in os.environ:
       # code that requires the API key
   else:
       print("Skipping - API_KEY not set")
   ```

4. **Use try/except** for optional imports:
   ```python
   try:
       from optional_package import Client  # type: ignore[import-not-found]
       # use Client
   except ImportError:
       print("Optional package not installed - skipping")
   ```

### Common false positives from ty

The SDK's gateway methods return `object` type, causing false positives when accessing dict keys:
- `error[non-subscriptable]` - Add `# type: ignore[index]`
- `error[not-iterable]` - Add `# type: ignore[union-attr]`
- `error[unsupported-operator]` - Add `# type: ignore[operator]`

## Markers

Only notebooks with the `@nemo-nb: process` marker will be linted.
