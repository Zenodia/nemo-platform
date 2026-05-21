# NeMo Platform Docs

The documentation site is built with MkDocs from the repository-root
`mkdocs.yml` and the source files in this `docs/` directory. The generated site
is written to `../site/`.

For contribution process details, see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Prerequisites

- Python 3.11 or later. Verify with `python3 --version`. See the
  [Python downloads](https://www.python.org/downloads/) page for installation
  options.
- [uv](https://docs.astral.sh/uv/). Verify with `uv --version`.
- GNU Make. Verify with `make --version`.
- Bash and a POSIX-like shell environment for the helper scripts.

MkDocs and the required plugins are installed into `docs/.venv-mkdocs` from
`docs/requirements-mkdocs.txt`:

```bash
make -C docs env
```

Node.js and npm are not required for the current MkDocs workflow.

## Local Development

Set up the docs-local virtual environment:

```bash
make -C docs env
```

Serve the site with live reload:

```bash
make -C docs live
```

Build the site with the same strict MkDocs mode used by CI:

```bash
make -C docs publish
```

Use another local port if `8000` is already in use:

```bash
LIVE_DOCS_PORT=8001 make -C docs live
```

To include pages that are temporarily hidden by `extra.hidden_docs` in
`mkdocs.yml`, use:

```bash
make -C docs live-with-unready
make -C docs html-with-unready
```

## Useful Checks

Check supported JSON and Python fenced code blocks:

```bash
make -C docs check-code-blocks
```

Apply the formatter for supported code blocks:

```bash
make -C docs format-code-blocks
```

Lint selected notebook-style docs:

```bash
make -C docs lint-python
```

## Generated References

Regenerate CLI and config reference docs from the repository root:

```bash
make generate-cli-reference-docs
make generate-config-reference-docs
```

The REST API page at `docs/api/index.md` renders
`docs/api/openapi.yaml`, which is a tracked symlink to
`../openapi/openapi.yaml`.

## Directory Layout

For the docs tree reference, see
[`CONTRIBUTING.md#directory-layout`](CONTRIBUTING.md#directory-layout).

MkDocs excludes this README and other docs-maintenance files from the published
site through `exclude_docs` in `mkdocs.yml`.
