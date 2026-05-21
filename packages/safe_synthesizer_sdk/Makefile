NMP_ROOT_PATH := $(shell git rev-parse --show-toplevel)

.PHONY: vendor-only
vendor-only:
	rm -r sdk/python/nemo-platform/src/nemo_platform/beta/safe_synthesizer/ || true
	cd ${NMP_ROOT_PATH} && uv run --no-sync nemo-platform-sdk-tools vendor from-config safe_synthesizer_sdk

.PHONY: vendor
vendor: vendor-only
	cd ${NMP_ROOT_PATH} && uv run --no-sync nemo-platform-sdk-tools post-generation update-license-headers
