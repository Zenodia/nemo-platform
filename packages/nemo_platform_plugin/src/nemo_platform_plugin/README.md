# nemo-platform-plugin

`nemo-platform-plugin` is the only package NeMo Platform plugin authors install. It re-exports all base classes, schemas, and utilities needed to build fully-featured NeMo Platform plugins.

## Surfaces

| Surface | Base class | Entry-point group | Purpose |
|---|---|---|---|
| HTTP service | `NemoService` | `nemo.services` | Contributes FastAPI routers mounted at `/apis/<name>/...` |
| CLI | `NemoCLI` | `nemo.cli` | Contributes `nemo <name> <cmd>` subcommands |
| Job | `NemoJob` | `nemo.jobs` | Contributes schedulable, container-executable jobs. Auto-generates `run` / `submit` / `explain` CLI verbs. |
| Controller | `NemoController` | `nemo.controllers` | Contributes background reconcile-loop controllers |
| Configuration | `NemoConfig` | (none)¹ | Typed plugin configuration with env var / YAML loading |
| Entity | `NemoEntity` | (none)¹ | Entity definitions stored in the NeMo Platform entity store |

¹ Not discovered via entry-points — used directly by plugin code.

## Installation

```bash
uv add nemo-platform-plugin nemo-platform
```

`nemo-platform` is required for entity client injection at runtime.

## How plugins are discovered

Declare surfaces in `pyproject.toml` entry-point groups. Install the package and the platform picks them up at startup — no registration code needed. See [QUICKSTART.md](docs/QUICKSTART.md) for the full template.

## The `name` rule

Every surface class requires a non-empty `name: ClassVar[str]`. Checked at class-definition time — missing raises `TypeError`. Must exactly match the entry-point key; mismatch logs a warning at startup.

## Next steps

- [QUICKSTART.md](docs/QUICKSTART.md) — build your first plugin end-to-end
- [SERVICE.md](docs/SERVICE.md) — HTTP routes, CRUD patterns, testing
- [JOB.md](docs/JOB.md) — jobs, CLI commands, auto-generated job commands
- [CONTROLLER.md](docs/CONTROLLER.md) — reconcile loops, state machines, service principal
- [CONFIG.md](docs/CONFIG.md) — typed configuration, env vars, YAML, test overrides
- [ENTITY.md](docs/ENTITY.md) — entity store, CRUD client, pagination, optimistic locking
- [INFERENCE_MIDDLEWARE.md](docs/INFERENCE_MIDDLEWARE.md) — inference request/response middleware, typed bodies, and response annotations
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — discovery, startup, all surfaces, SDK surface
