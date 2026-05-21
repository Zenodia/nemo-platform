
UV ?= uv
CI_PROJECT_DIR ?= $(shell git rev-parse --show-toplevel)
NMP_BASE_URL ?= http://localhost:8080

.PHONY: help
help:
	@echo "Makefile commands:"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

ensure-jobs-binary: ## Ensure the jobs-launcher binary is built, for logs
	cd $(CI_PROJECT_DIR)/services/core/jobs/jobs-launcher/ && \
	ls jobs-launcher || \
	./build-manual.sh

.PHONY: quickstart-up
up: quickstart-up

quickstart-up: ## Start the NeMo Platform with core services for local development
	cd $(CI_PROJECT_DIR) && \
	NMP_CONFIG_FILE_PATH=$(CI_PROJECT_DIR)/packages/nmp_platform/config/local.yaml \
	EXTRA_LOG_CONFIG='{loggers: {nmp.core.models.controllers.backends.docker: {level: DEBUG}}}' \
	DATABASE_DIALECT=sqlite \
	DATABASE_PATH=/tmp/nmp-platform.db \
	UVICORN_RELOAD=true \
	$(UV) run nemo services run \
	--services models,entities,jobs,secrets,files,auth,safe-synthesizer,inference-gateway \
	--controllers jobs,models

quickstart-clean: ## Clean the NeMo Platform DB
	rm -rf /tmp/nmp-platform.db
	
setup-model-filesets: ## Setup model filesets in the Files API
	PYTHONUNBUFFERED=1 $(UV) run python scripts/setup_model_filesets.py \
		--files-api-url $(NMP_BASE_URL) \
		--workspace default

run-e2e-test: setup-model-filesets ## Run the e2e test notebook with PII and synthetic data after starting quickstart
	PYTHONUNBUFFERED=1 $(UV) run papermill tests/notebooks/test_nss_job.ipynb \
		 --log-output -p csv_filepath tests/notebooks/womens-clothing-ecommerce.csv out.executed.ipynb

run-e2e-test-synth-only: setup-model-filesets ## Run the e2e test notebook with synthetic data only after starting quickstart
	PYTHONUNBUFFERED=1 SKIP_PII_REPLACEMENT=true $(UV) run papermill tests/notebooks/test_nss_job.ipynb \
		 --log-output -p csv_filepath tests/notebooks/womens-clothing-ecommerce.csv out.executed.ipynb

run-e2e-test-pii-only: setup-model-filesets ## Run the e2e test notebook with PII only after starting quickstart
	PYTHONUNBUFFERED=1 SKIP_SYNTHESIS=true $(UV) run papermill tests/notebooks/test_nss_job.ipynb \
		 --log-output -p csv_filepath tests/notebooks/womens-clothing-ecommerce.csv out.executed.ipynb

run-e2e-test-transform-only: setup-model-filesets ## Run the e2e test notebook with transform only after starting quickstart
	PYTHONUNBUFFERED=1 TRANSFORM_ONLY=true $(UV) run papermill tests/notebooks/test_nss_job.ipynb \
		 --log-output -p csv_filepath tests/notebooks/womens-clothing-ecommerce.csv out.executed.ipynb

build-initial-image: ## Build the nmp-gpu-tasks base image (tagged as :initial)
	cd ../.. && BAKE_TAG=initial docker buildx bake \
	--set *.platform=linux/amd64 --load docker-gpu

build-dev-image: ensure-jobs-binary ## Build an image that copies over just code changes
	cd ../.. && docker buildx build --builder default -f services/safe-synthesizer/Dockerfile.dev \
	--build-arg BASE_IMAGE=my-registry/nmp-gpu-tasks:initial \
	-t my-registry/nmp-gpu-tasks:local \
	--load \
	.

clean-quickstart: ## Clean the NeMo Platform DB and files from tmp
	rm -rf /tmp/nmp-*

# ============================================================================
# nemo-safe-synthesizer local development
# ============================================================================
# The nemo-safe-synthesizer package is resolved through the project's
# configured package indexes. For local development when iterating on NSS
# changes, use `make use-nss-local` to switch to a locally-built wheel.
# Revert local package-source changes before committing.

NSS_REPO_URL ?= git@github.com:NVIDIA/nemo-safe-synthesizer.git
NSS_REPO_REF ?= main
NSS_WHEEL_DIR := $(CI_PROJECT_DIR)/packages/nemo_safe_synthesizer_wheel
NSS_REPO_PATH :=  $(CI_PROJECT_DIR)/../Safe-Synthesizer

.nss_repo:
	if [ ! -d "$(NSS_REPO_PATH)" ]; then \
		echo "Error: $(NSS_REPO_PATH) directory not found. Please clone the repository first."; \
		echo "Or export NSS_REPO_PATH to the path of the repository first."; \
		exit 1; \
	else \
		ln -s $(NSS_REPO_PATH) .nss_repo; \
	fi

.PHONY: use-nss-local
use-nss-local: .nss_repo ## Build nemo-safe-synthesizer from source and use local wheel
	@mkdir -p $(NSS_WHEEL_DIR)
	if [ ! -d ".nss_repo" ]; then \
		echo "Error: .nss_repo directory not found. Please clone the repository first."; \
		exit 1; \
	fi
	cd .nss_repo/ && git fetch && git checkout $(NSS_REPO_REF) && git pull
	rm -f $(NSS_WHEEL_DIR)/*.whl
	cd $(NSS_REPO_PATH) && uv lock && uv build --wheel
	cp $(NSS_REPO_PATH)/dist/*.whl $(NSS_WHEEL_DIR)/
	$(eval NSS_WHEEL := $(notdir $(wildcard $(NSS_WHEEL_DIR)/*.whl)))
	@echo "Wheel built: $(NSS_WHEEL)"
	@echo "Switching pyproject.toml to local wheel..."
	sed -i'' -E 's|nemo-safe-synthesizer = \{[^}]*\}|nemo-safe-synthesizer = { path = "$(NSS_WHEEL_DIR)/$(NSS_WHEEL)" }|' $(CI_PROJECT_DIR)/pyproject.toml
	sed -i'' -E 's|nemo-safe-synthesizer = \{[^}]*\}|nemo-safe-synthesizer = { path = "$(NSS_WHEEL_DIR)/$(NSS_WHEEL)" }|' $(CI_PROJECT_DIR)/services/safe-synthesizer/pyproject.toml
	cd $(CI_PROJECT_DIR) && uv lock
	@echo "Run 'make bootstrap-nss' to update."
