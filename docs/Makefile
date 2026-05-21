# Makefile targets for MkDocs documentation

.PHONY: help env mkdocs-env html html-fast html-with-unready mkdocs-html \
	publish mkdocs-publish live live-fast live-with-unready mkdocs-live \
	clean mkdocs-clean format-code-blocks check-code-blocks sync lint-python deploy-pages \
	deploy-pr-preview delete-pr-preview mkdocs-version require-pr-number

# Fix locale if current setting is unsupported (common in containers).
ifeq ($(shell locale 2>&1 | grep -q "Cannot set" && echo broken),broken)
export LC_ALL=C
endif

# Usage:
#   make html                          # Build documentation with MkDocs
#   make html-with-unready             # Build with temporarily hidden docs included
#   make live                          # Live server with auto-reload
#   make live-with-unready             # Live server with temporarily hidden docs included
#   make publish                       # Production build (strict)

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
MKDOCS_ROOT = $(MAKEFILE_DIR)..
SITE_DIR = $(MKDOCS_ROOT)/site
VENV_MKDOCS = $(MAKEFILE_DIR).venv-mkdocs
VENV_MKDOCS_BIN = $(VENV_MKDOCS)/bin
VENV_PYTHON = $(VENV_MKDOCS_BIN)/python
MKDOCS = $(VENV_MKDOCS_BIN)/mkdocs
MIKE = $(VENV_MKDOCS_BIN)/mike
LIVE_DOCS_HOST ?= 127.0.0.1
LIVE_DOCS_PORT ?= 8000
PAGES_BRANCH ?= gh-pages
DOCS_SITE_URL ?= https://nvidia-nemo.github.io/nemo-platform/latest/
DOCS_CANONICAL_VERSION ?= latest
DOCS_VERSION ?= main
DOCS_ALIAS ?= latest
PR_PREVIEW_VERSION = pr-$(PR_NUMBER)
PR_PREVIEW_PREFIX = pr-preview/$(PR_PREVIEW_VERSION)
PR_PREVIEW_SITE_URL ?= $(DOCS_SITE_URL)$(PR_PREVIEW_PREFIX)/
PR_PREVIEW_CANONICAL_VERSION ?= $(PR_PREVIEW_VERSION)
export PATH := $(VENV_MKDOCS_BIN):$(HOME)/.local/bin:$(PATH)

help:
	@echo "Makefile commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

env: mkdocs-env ## Set up the documentation virtualenv

mkdocs-env: ## Set up the MkDocs virtualenv
	cd $(MAKEFILE_DIR) && bash _scripts/setup_mkdocs_env.sh

html-fast: html ## Build documentation with MkDocs

html: mkdocs-html ## Build documentation with MkDocs

html-with-unready: mkdocs-env ## Build documentation with temporarily hidden docs included
	@echo "Building with MkDocs, including temporarily hidden docs..."
	cd $(MKDOCS_ROOT) && NMP_HIDE_UNREADY_DOCS=false $(MKDOCS) build --strict --config-file mkdocs.yml

mkdocs-html: mkdocs-env ## Build documentation with MkDocs
	@echo "Building with MkDocs..."
	cd $(MKDOCS_ROOT) && $(MKDOCS) build --strict --config-file mkdocs.yml

publish: mkdocs-publish ## Build production documentation with MkDocs

mkdocs-publish: mkdocs-env ## Build production documentation with MkDocs in strict mode
	@echo "Publishing with MkDocs..."
	cd $(MKDOCS_ROOT) && $(MKDOCS) build --config-file mkdocs.yml --strict

live-fast: live ## Start the MkDocs live-reload server

live: mkdocs-live ## Start the MkDocs live-reload server

live-with-unready: mkdocs-env ## Start the live server with temporarily hidden docs included
	@echo "Starting MkDocs live server, including temporarily hidden docs..."
	cd $(MKDOCS_ROOT) && NMP_HIDE_UNREADY_DOCS=false $(MKDOCS) serve --config-file mkdocs.yml --dev-addr $(LIVE_DOCS_HOST):$(LIVE_DOCS_PORT)

mkdocs-live: mkdocs-env ## Start the MkDocs live-reload server
	@echo "Starting MkDocs live server..."
	cd $(MKDOCS_ROOT) && $(MKDOCS) serve --config-file mkdocs.yml --dev-addr $(LIVE_DOCS_HOST):$(LIVE_DOCS_PORT)

clean: mkdocs-clean ## Remove documentation build artifacts and virtualenv

mkdocs-clean: ## Remove MkDocs build artifacts and virtualenv
	rm -rf $(SITE_DIR) $(VENV_MKDOCS)

format-code-blocks: mkdocs-env ## Autoformat supported fenced code blocks
	@echo "Formatting supported code blocks in markdown files..."
	cd $(MAKEFILE_DIR) && $(VENV_PYTHON) _scripts/format_code_blocks.py --docs-dir $(MAKEFILE_DIR)

check-code-blocks: mkdocs-env ## Check supported fenced code blocks are formatted
	@echo "Checking supported code block formatting..."
	cd $(MAKEFILE_DIR) && $(VENV_PYTHON) _scripts/format_code_blocks.py --docs-dir $(MAKEFILE_DIR) --check

sync: ## Sync files from documentation/docs/ into docs/
	@echo "Syncing files from documentation/docs/ to docs/..."
	@rsync -av $(MAKEFILE_DIR)/../documentation/docs/ $(MAKEFILE_DIR)
	@rm -rf $(MAKEFILE_DIR)/../documentation/docs/
	@echo "Sync complete"

lint-python: mkdocs-env ## Lint selected notebooks and run type checking
	@echo "Linting Python code in notebooks..."
	cd $(MAKEFILE_DIR) && $(VENV_PYTHON) _scripts/lint_notebooks.py run-inference/ safe-synthesizer/ --type-check

deploy-pages: mkdocs-env ## Deploy main docs to GitHub Pages with mike
	@echo "Deploying $(DOCS_VERSION) docs to $(PAGES_BRANCH) with alias $(DOCS_ALIAS)..."
	cd $(MKDOCS_ROOT) && NMP_DOCS_SITE_URL="$(DOCS_SITE_URL)" NMP_DOCS_CANONICAL_VERSION="$(DOCS_CANONICAL_VERSION)" $(MIKE) deploy --push --update-aliases --alias-type redirect \
		--config-file mkdocs.yml --branch $(PAGES_BRANCH) $(DOCS_VERSION) $(DOCS_ALIAS)
	cd $(MKDOCS_ROOT) && NMP_DOCS_SITE_URL="$(DOCS_SITE_URL)" NMP_DOCS_CANONICAL_VERSION="$(DOCS_CANONICAL_VERSION)" $(MIKE) set-default --push --config-file mkdocs.yml \
		--branch $(PAGES_BRANCH) $(DOCS_ALIAS)

deploy-pr-preview: require-pr-number mkdocs-env ## Deploy a PR preview to GitHub Pages with mike
	@echo "Deploying PR preview $(PR_PREVIEW_VERSION) under $(PR_PREVIEW_PREFIX)..."
	cd $(MKDOCS_ROOT) && NMP_DOCS_SITE_URL="$(PR_PREVIEW_SITE_URL)" NMP_DOCS_CANONICAL_VERSION="$(PR_PREVIEW_CANONICAL_VERSION)" $(MIKE) deploy --push --update-aliases --alias-type redirect \
		--config-file mkdocs.yml --branch $(PAGES_BRANCH) --deploy-prefix $(PR_PREVIEW_PREFIX) \
		--title "PR #$(PR_NUMBER)" $(PR_PREVIEW_VERSION)
	cd $(MKDOCS_ROOT) && NMP_DOCS_SITE_URL="$(PR_PREVIEW_SITE_URL)" NMP_DOCS_CANONICAL_VERSION="$(PR_PREVIEW_CANONICAL_VERSION)" $(MIKE) set-default --push --config-file mkdocs.yml \
		--branch $(PAGES_BRANCH) --deploy-prefix $(PR_PREVIEW_PREFIX) $(PR_PREVIEW_VERSION)

delete-pr-preview: require-pr-number mkdocs-env ## Delete a PR preview from GitHub Pages
	@echo "Deleting PR preview $(PR_PREVIEW_VERSION) from $(PR_PREVIEW_PREFIX)..."
	cd $(MKDOCS_ROOT) && $(MIKE) delete --push --config-file mkdocs.yml \
		--branch $(PAGES_BRANCH) --deploy-prefix $(PR_PREVIEW_PREFIX) --all || true

mkdocs-version: deploy-pages ## Deploy a versioned release with mike

require-pr-number:
	@test -n "$(PR_NUMBER)" || (echo "PR_NUMBER is required" && exit 1)
