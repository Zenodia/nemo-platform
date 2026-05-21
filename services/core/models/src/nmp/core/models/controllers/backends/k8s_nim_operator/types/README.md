# NIM Operator Types

This directory contains Pydantic models automatically generated from the NVIDIA k8s-nim-operator Kubernetes CRD definitions.

## Overview

These models provide native Python/Pydantic representations of the `NIMService` and `NIMCache` Custom Resource Definitions (CRDs) from the [k8s-nim-operator](https://github.com/NVIDIA/k8s-nim-operator) project. This allows us to:

1. **Type-safe model definitions**: Use Pydantic for validation and IDE autocomplete when working with NIM operator resources
2. **Compile ModelDeploymentConfigs to NIMService**: Transform our internal ModelDeploymentConfig specs into valid NIMService Kubernetes resources
3. **Stay in sync**: Regenerate types when the upstream operator CRDs change

## Generated Files

- `nimservice.py` - Pydantic models for the `NIMService` CRD (~2700 lines)
- `nimcache.py` - Pydantic models for the `NIMCache` CRD (~580 lines)
- `__init__.py` - Package exports

## Regenerating Types

When the k8s-nim-operator CRDs are updated, you can regenerate the Pydantic models using the provided script.

### List Available Versions

To see all available versions (tags) from the k8s-nim-operator repository:

```bash
cd services/core/infrastructure/models
./scripts/update-types.sh
```

This will clone the repository (if needed), list the most recent versions, and leave the repository for inspection.

### Generate from Specific Version

To generate types from a specific version:

```bash
cd services/core/infrastructure/models

# Generate types from a specific version
uv run ./scripts/update-types.sh --version v2.0.2
```

This will:

1. Clone or update the k8s-nim-operator repository
2. Checkout the specified version tag
3. Extract the OpenAPI v3 schemas from the CRD YAML files
4. Use `datamodel-code-generator` to create Pydantic v2 models
5. Clean up the cloned repository

### Importing the Models

```python
from models.nim_operator_types import NIMService, NIMCache
```

### Creating a NIMService

```python
from models.nim_operator_types import NIMService

nim_service = NIMService(
    apiVersion="apps.nvidia.com/v1alpha1",
    kind="NIMService",
    metadata={
        "name": "my-llm-service",
        "namespace": "default"
    },
    spec={
        "image": {
            "repository": "nvcr.io/nim/meta/llama-3.1-8b-instruct",
            "tag": "1.0.0"
        },
        "authSecret": "ngc-api-key",
        "replicas": 2,
        "resources": {
            "limits": {
                "nvidia.com/gpu": "1"
            }
        }
    }
)

# Serialize to JSON for Kubernetes API
k8s_manifest = nim_service.model_dump_json(exclude_none=True)
```

### Creating a NIMCache

```python
from models.nim_operator_types import NIMCache

nim_cache = NIMCache(
    apiVersion="apps.nvidia.com/v1alpha1",
    kind="NIMCache",
    metadata={
        "name": "my-llm-cache",
        "namespace": "default"
    },
    spec={
        "source": {
            "ngc": {
                "authSecret": "ngc-api-key",
                "modelPuller": "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.0.0",
                "model": {
                    "profiles": ["profile-a"]
                }
            }
        },
        "storage": {
            "pvc": {
                "create": True,
                "size": "50Gi",
                "storageClass": "fast-ssd"
            }
        }
    }
)
```


### Testing the Generated Models

After regenerating, test that the models work correctly:

```bash
uv run python test_nim_types.py
```

## Upstream Source

- **Repository**: https://github.com/NVIDIA/k8s-nim-operator
- **CRD Definitions**: `config/crd/bases/`
  - `apps.nvidia.com_nimservices.yaml`
  - `apps.nvidia.com_nimcaches.yaml`

## Development Dependencies

The generation process requires:
- `datamodel-code-generator>=0.26.2` (for generating Pydantic models from OpenAPI schemas)
- `pyyaml>=6.0.2` (for parsing CRD YAML files)

These are included in the `dev` dependency group in `pyproject.toml`.
