# Documentation Contributions

This repository builds the NeMo Platform documentation with MkDocs. The current
source of truth is the root [`mkdocs.yml`](../mkdocs.yml), the documentation
source tree under [`docs/`](.), and the targets in [`docs/Makefile`](Makefile).

Do not recreate the old Sphinx release flow as part of normal documentation
work. In particular, `docs/conf.py` and `docs/versions1.json` are gone, and
`docs/requirements-docs.txt` has been removed.

## Current Stack

- **Source:** Markdown, notebooks, snippets, images, and assets under `docs/`.
- **Config:** `mkdocs.yml` at the repository root.
- **Theme:** Material for MkDocs with local overrides in `docs/_overrides/`.
- **Environment:** `docs/.venv-mkdocs`, created by `make -C docs env`.
- **Dependencies:** `docs/requirements-mkdocs.txt`.
- **Build output:** `site/`.
- **Versioning and deploys:** `mike` publishes versioned docs to the `gh-pages`
  branch through `docs/Makefile` targets.
- **CI:** `.github/workflows/docs.yaml` builds docs when `docs/**`,
  `mkdocs.yml`, or `openapi/openapi.yaml` changes.

The docs environment is intentionally separate from the main Python workspace.
The setup script uses `uv --no-config` to create and populate `.venv-mkdocs`.
Use the Make targets rather than installing MkDocs packages into the repo
environment by hand.

## Directory Layout

- `api/`: REST API landing page.
- `assets/`, `images/`, `stylesheets/`, `javascripts/`: MkDocs assets.
- `_hooks/`: MkDocs hook modules.
- `_overrides/`: Material for MkDocs theme overrides.
- `_scripts/`: docs helper scripts.
- `_snippets/`: reusable Markdown fragments that are included by pages.
- Feature directories such as `get-started/`, `guardrails/`, `evaluator/`,
  `customizer/`, and `safe-synthesizer/`: published documentation content.

## Local Commands

Run docs commands from the repository root unless otherwise noted.

```bash
make -C docs env
make -C docs live
make -C docs html
```

Useful variants:

```bash
# Use another port if 8000 is busy.
LIVE_DOCS_PORT=8001 make -C docs live

# Build or serve pages that are currently hidden from normal output.
make -C docs html-with-unready
make -C docs live-with-unready

# Run the same strict MkDocs build used by CI.
make -C docs publish

# Remove generated docs output and the MkDocs virtualenv.
make -C docs clean
```

Before opening or updating a PR, run the strict build:

```bash
make -C docs publish
```

For changes that include JSON or Python fenced code blocks, also run:

```bash
make -C docs check-code-blocks
```

To apply the supported code-block formatter:

```bash
make -C docs format-code-blocks
```

For changes that touch notebooks or Python examples in the linted docs areas,
run:

```bash
make -C docs lint-python
```

## Authoring Guidelines

Add pages under the relevant `docs/` section and update the explicit `nav:`
block in `mkdocs.yml`. Pages that are not listed in `nav:` can still build, but
they will not appear in the published navigation unless linked from another
page.

Use `index.md` for section landing pages. Keep section names and file names
stable when possible because redirects and external links may depend on them.
If you rename or move a published page, add a redirect in the `redirects` plugin
configuration in `mkdocs.yml`.

Use MkDocs-supported Markdown, not Sphinx-only directives. The active extensions
include admonitions, details blocks, tabbed content, Mermaid fences, tables,
footnotes, definition lists, task lists, snippets, and syntax highlighting.

Use substitutions from the `extra:` block in `mkdocs.yml`, such as
`{{ platform_name }}` or `{{ release }}`. Add new shared product names and
versions there instead of hard-coding them across many pages.

Place reusable Markdown fragments under `_snippets/`. Snippet files are excluded
as standalone pages and are intended to be included from real pages with the
configured snippets extension.

Put static assets under the existing docs asset directories. Image assets under
`docs/images/**` are fetched with Git LFS in CI. If local images render as tiny
text pointer files, run:

```bash
git lfs pull --include="docs/images/**" --exclude=""
```

Notebooks are rendered by `mkdocs-jupyter` with execution disabled. Keep checked
in notebook output deliberate, small, and reviewable.

## Generated Material

Some docs are generated from code or OpenAPI output. Regenerate them from the
repo root instead of hand-editing generated files.

```bash
make generate-cli-reference-docs
make generate-config-reference-docs
```

The API reference page uses `docs/api/openapi.yaml`, a tracked symlink to
`openapi/openapi.yaml`. When API routes, schemas, or service models change,
follow the repository SDK/OpenAPI workflow and regenerate the OpenAPI spec before
building the docs.

The Python SDK reference is rendered through `mkdocstrings` from
`sdk/python/nemo-platform/src`. If SDK-facing API changes affect the docs, follow
the repository SDK generation process rather than editing generated SDK output
by hand.

## Hidden Docs

Some pages are temporarily gated by `extra.hidden_docs` in `mkdocs.yml` and the
`docs/_hooks/hide_unready_docs.py` hook. In normal builds, the hook removes
matching nav entries, source files, inline links, and API filter chips.

Use the `with-unready` targets to inspect hidden docs locally:

```bash
make -C docs live-with-unready
make -C docs html-with-unready
```

When a hidden area becomes ready, update `extra.hidden_docs` in `mkdocs.yml`
rather than deleting files or working around the hook from individual pages.

## CI And Publishing

The Documentation workflow runs `make -C docs publish` and uploads the `site/`
directory as a `docs-site` artifact.

For pull requests from branches in the same repository, the workflow also
deploys a PR preview under GitHub Pages by using `make -C docs deploy-pr-preview`.
Pull requests from forks receive the build artifact but do not deploy a preview.

Pushes to `main` deploy the `main` docs version with the `latest` alias. Tag
builds derive the docs version from the tag name, stripping an optional `docs/`
prefix and an optional leading `v`, then deploy that version with the `latest`
alias.

Manual publishing uses these targets:

```bash
make -C docs deploy-pages
PR_NUMBER=<number> make -C docs deploy-pr-preview
PR_NUMBER=<number> make -C docs delete-pr-preview
```

Deployment targets push to `gh-pages`; do not run them casually from a local
branch.

## PR Expectations

Keep docs updates in the same PR as the user-facing code change when that is the
fastest way to keep behavior and documentation in sync. For larger features,
draft the initial technical content near the code change and ask the docs owners
for review.

For navigation moves, new top-level sections, broad terminology changes, or
anything that changes the information architecture, coordinate with the docs
owners before reshaping the tree.

For small fixes, update the relevant Markdown directly and include the local
`make -C docs publish` result in the PR description.

## Troubleshooting

If `make -C docs live` fails because the port is already in use, set
`LIVE_DOCS_PORT`:

```bash
LIVE_DOCS_PORT=8001 make -C docs live
```

If the docs virtualenv appears stale, rebuild it:

```bash
make -C docs clean
make -C docs env
```

If a strict build reports missing files, check the `nav:` entries, redirects,
snippet includes, and hidden-doc patterns in `mkdocs.yml`.

If API docs look stale, regenerate `openapi/openapi.yaml` through the repository
OpenAPI workflow and confirm that `docs/api/openapi.yaml` still points to it.

If CI reports that a docs image is a Git LFS pointer, fetch the image content
with Git LFS and recommit the real asset state.
