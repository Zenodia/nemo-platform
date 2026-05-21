NMP_ROOT_PATH := $(shell dirname $(shell dirname $(shell pwd)))

.PHONY: vendor-only
vendor-only:
	@echo "📦 Vendoring models to nemo-platform SDK..."
	cd ${NMP_ROOT_PATH} && uv run --no-sync nemo-platform-sdk-tools vendor from-config models

.PHONY: vendor
vendor: vendor-only
	cd ${NMP_ROOT_PATH} && uv run --no-sync nemo-platform-sdk-tools post-generation update-license-headers
