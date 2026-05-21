# NeMo Data Designer Plugin

A NeMo Platform plugin that brings Data Designer into the platform.

## Nemotron Personas Filesets

When executing remotely, Data Designer workloads that include `PersonSampler` columns require Nemotron Personas filesets to exist in the `system` workspace for each requested locale. These filesets can be created using the CLI.

Use an existing NGC API key secret:

```bash
nemo data-designer personas make-fileset \
  --locale en_US \
  --api-key-secret system/ngc-api-key
```

Create a new secret from an environment variable, then bind the fileset to it:

```bash
nemo data-designer personas make-fileset \
  --locale en_US \
  --api-key-secret system/my-ngc-key \
  --api-key-env-var NGC_API_KEY
```
