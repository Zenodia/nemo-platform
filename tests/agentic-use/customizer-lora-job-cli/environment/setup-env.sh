#!/bin/bash
set -e

echo '=== Pre-pulling training image ==='
if command -v docker &> /dev/null && [ -S /var/run/docker.sock ]; then
    # The customizer dispatches training jobs using this image
    # gpu-finetune-test:latest must be pre-built on the host
    docker image inspect gpu-finetune-test:latest > /dev/null 2>&1 && \
        echo 'gpu-finetune-test:latest found' || \
        echo 'WARNING: gpu-finetune-test:latest not found - build it with: docker build -f tests/agentic-use/gpu-direct-lora-finetune-cli/environment/Dockerfile -t gpu-finetune-test:latest .'
else
    echo 'WARNING: Docker not available'
fi

echo '=== Creating workspace ==='
/app/.venv/bin/nmp workspaces create --name lora-training-workspace || echo 'Workspace may already exist'

echo '=== Registering model entity ==='
# Register a model entity that the customizer can reference.
# The model name is what users pass to the customizer API.
/app/.venv/bin/nmp models create --workspace lora-training-workspace \
    --input-data '{
        "name": "smollm-135m",
        "spec": {
            "num_parameters": 135000000,
            "is_chat": false,
            "family": "smollm"
        },
        "custom_fields": {
            "hf_model_id": "HuggingFaceTB/SmolLM-135M"
        }
    }' 2>&1 || echo 'Model may already exist'

echo '=== Environment setup complete ==='
