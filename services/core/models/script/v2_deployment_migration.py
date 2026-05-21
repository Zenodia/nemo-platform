#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "nemo-microservices==1.5.0",
#   "nemo-platform>=2.0.0.dev0,<2.1.0",
# ]
# ///
"""
Migrate V1 model deployments to V2 deployment configs and deployments.

This script follows a four-phase workflow:
1) setup: validate credentials/endpoints and optional connectivity checks
2) plan: discover READY V1 deployments and generate a migration plan JSON
3) apply: execute a generated plan by creating V2 model entities, deployment configs, and deployments
4) verify: send a "hello world" chat completion to each deployed model to confirm reachability

Field mapping (V1 → V2):
  DeploymentConfig.namespace           → ModelDeploymentConfig.workspace
  DeploymentConfig.name                → ModelDeploymentConfig.name (prefixed if --target-workspace)
  DeploymentConfig.description         → ModelDeploymentConfig.description
  DeploymentConfig.model (str ref)     → ModelDeploymentConfig.model_entity_id
  NIMDeploymentConfig.gpu              → NIMDeployment.gpu
  NIMDeploymentConfig.image_name       → NIMDeployment.image_name
  NIMDeploymentConfig.image_tag        → NIMDeployment.image_tag
  NIMDeploymentConfig.additional_envs  → NIMDeployment.additional_envs
  NIMDeploymentConfig.pvc_size         → NIMDeployment.disk_size (rename)
  NIMDeploymentConfig.disable_lora_support → NIMDeployment.lora_enabled (inverted)
  NIMDeploymentConfig.namespace (k8s)  → (dropped; V2 uses k8s_nim_operator_config)
  DeploymentConfig.external_endpoint   → (skipped; register via inference gateway instead)
  ModelDeployment.namespace            → ModelDeployment.workspace
  ModelDeployment.name                 → ModelDeployment.name (prefixed if --target-workspace)
  ModelDeployment.async_enabled        → (dropped; no V2 equivalent)

Model entity field mapping (V1 → V2):
  Model.namespace      → ModelEntity.workspace
  Model.name           → ModelEntity.name (invalid chars replaced with '-')
  Model.description    → ModelEntity.description
  Model.spec           → ModelEntity.spec
  Model.base_model     → ModelEntity.base_model
  Model.api_endpoint   → ModelEntity.api_endpoint
  Model.custom_fields  → ModelEntity.custom_fields
  Model.model_providers → ModelEntity.model_providers
  Model.ownership      → ModelEntity.ownership
  Model.project        → ModelEntity.project
  Model.prompt         → ModelEntity.prompt
  Model.peft.finetuning_type → ModelEntity.finetuning_type
  Model.artifact       → (skipped; fileset migration requires separate step)
  Model.peft.lora/p_tuning → (skipped; adapter migration requires separate step)

Only deployments with status READY are included in the plan.

When --target-workspace is set, all namespaces are merged into a single workspace and names
are prefixed with '<v1-namespace>-' to avoid collisions.

Usage examples:
  nemo auth login --base-url <your-v2-base-url>   # if V2 auth is enabled
  uv run v2_deployment_migration.py setup --check --namespace <namespace>
  uv run v2_deployment_migration.py plan --plan plan.json
  uv run v2_deployment_migration.py plan --namespace <ns> --plan plan.json
  uv run v2_deployment_migration.py plan --namespace-prefix <prefix> --plan plan.json
  uv run v2_deployment_migration.py apply --plan plan.json
  uv run v2_deployment_migration.py apply --plan plan.json --dry-run
  # Optional: merge all namespaces into one workspace (names get prefixed)
  uv run v2_deployment_migration.py apply --target-workspace <workspace> --plan plan.json
  uv run v2_deployment_migration.py verify --plan plan.json
  uv run v2_deployment_migration.py verify --plan plan.json --timeout 120

Dependencies are embedded above for uv script execution.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import nemo_microservices
import nemo_platform
from nemo_microservices import NeMoMicroservices
from nemo_platform import ConflictError, NeMoPlatform, NotFoundError

print("nemo_microservices", nemo_microservices.__version__)
print("nemo_platform", nemo_platform.__version__)

logger = logging.getLogger(__name__)

_READY_STATUS = "READY"


@dataclass
class RuntimeConfig:
    v1_base_url: str
    v1_api_key: str | None
    v2_base_url: str | None
    target_workspace: str | None


@dataclass
class NIMDeploymentPlan:
    gpu: int
    image_name: str | None
    image_tag: str | None
    disk_size: str | None
    lora_enabled: bool | None
    additional_envs: dict[str, str] | None


@dataclass
class ConfigPlan:
    v1_namespace: str
    v1_config_name: str
    v2_workspace: str
    v2_config_name: str
    nim_deployment: NIMDeploymentPlan | None
    model_entity_id: str | None
    description: str | None
    project: str | None
    skipped: bool
    skip_reason: str | None
    warnings: list[str] = field(default_factory=list)


@dataclass
class DeploymentPlan:
    v1_namespace: str
    v1_deployment_name: str
    v1_status: str
    v2_workspace: str
    v2_deployment_name: str
    v2_config_name: str
    project: str | None
    warnings: list[str] = field(default_factory=list)


@dataclass
class ModelEntityPlan:
    # V1 source
    v1_namespace: str
    v1_name: str
    # V2 target
    v2_workspace: str
    v2_name: str  # normalized: invalid chars replaced with '-'
    # Fields to carry over (None means absent in V1)
    description: str | None
    spec: dict[str, Any] | None
    base_model: str | None
    finetuning_type: str | None
    fileset: str | None  # V2 fileset ref derived from V1 artifact.files_url (workspace/name)
    files_repo_id: str | None  # raw HF repo_id (namespace/repo) from V1 artifact.files_url
    api_endpoint: dict[str, Any] | None
    custom_fields: dict[str, Any] | None
    model_providers: list[str] | None
    ownership: dict[str, Any] | None
    project: str | None
    prompt: dict[str, Any] | None
    skipped: bool
    skip_reason: str | None
    warnings: list[str] = field(default_factory=list)


def _now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()


def _get_v1_client(cfg: RuntimeConfig) -> NeMoMicroservices:
    kwargs: dict[str, Any] = {"base_url": cfg.v1_base_url}
    if cfg.v1_api_key:
        kwargs["api_key"] = cfg.v1_api_key
    return NeMoMicroservices(**kwargs)


def _get_v2_sdk(cfg: RuntimeConfig) -> NeMoPlatform:
    kwargs: dict[str, Any] = {}
    if cfg.v2_base_url:
        kwargs["base_url"] = cfg.v2_base_url
    return NeMoPlatform(**kwargs)


def _resolve_runtime_config(args: argparse.Namespace) -> RuntimeConfig:
    v1_base_url = args.v1_base_url or os.environ.get("NMP_V1_BASE_URL") or os.environ.get("NMP_BASE_URL")
    v1_api_key = args.v1_api_key or os.environ.get("NMP_V1_API_KEY")
    v2_base_url = args.v2_base_url or os.environ.get("NMP_V2_BASE_URL") or os.environ.get("NEMO_MICROSERVICES_BASE_URL")
    target_workspace = getattr(args, "target_workspace", None)

    if not v1_base_url:
        raise ValueError("Missing required V1 base URL. Provide --v1-base-url or set NMP_V1_BASE_URL.")

    return RuntimeConfig(
        v1_base_url=v1_base_url,
        v1_api_key=v1_api_key,
        v2_base_url=v2_base_url,
        target_workspace=target_workspace,
    )


def _resolve_v2_names(v1_namespace: str, v1_name: str, target_workspace: str | None) -> tuple[str, str]:
    """Return (v2_workspace, v2_name).

    When target_workspace is set all namespaces merge into one workspace and names
    are prefixed with '<v1_namespace>-' to avoid collisions.
    """
    if target_workspace:
        return target_workspace, f"{v1_namespace}-{v1_name}"
    return v1_namespace, v1_name


def _translate_nim_deployment(
    v1_nim: Any,
    warnings: list[str],
) -> NIMDeploymentPlan:
    """Translate a V1 NIMDeploymentConfig to a V2 NIMDeploymentPlan."""
    lora_enabled: bool | None = None
    if getattr(v1_nim, "disable_lora_support", None) is not None:
        lora_enabled = not v1_nim.disable_lora_support

    if getattr(v1_nim, "namespace", None):
        warnings.append(
            f"V1 NIMDeploymentConfig.namespace='{v1_nim.namespace}' (Kubernetes namespace) "
            "has no direct V2 equivalent and was dropped. "
            "Configure node placement via k8s_nim_operator_config if needed."
        )

    return NIMDeploymentPlan(
        gpu=v1_nim.gpu,
        image_name=getattr(v1_nim, "image_name", None) or None,
        image_tag=getattr(v1_nim, "image_tag", None) or None,
        disk_size=getattr(v1_nim, "pvc_size", None) or None,
        lora_enabled=lora_enabled,
        additional_envs=getattr(v1_nim, "additional_envs", None) or None,
    )


def _extract_model_entity_id(model_field: Any) -> str | None:
    """Extract a V2 model_entity_id string from a V1 model field (str or ModelDe object)."""
    if model_field is None:
        return None
    if isinstance(model_field, str):
        return model_field
    # ModelDe object — reconstruct as namespace/name if both are present.
    ns = getattr(model_field, "namespace", None)
    name = getattr(model_field, "name", None)
    if ns and name:
        return f"{ns}/{name}"
    if name:
        return name
    return None


_HF_DATASETS_PREFIX = "hf://datasets/"


def _sanitize_fileset_name(repo_id: str) -> str:
    """Convert a datastore repo_id into a V2 Files-service-safe fileset name.

    Mirrors the logic in services/core/files/script/v2_migration.py so that the
    name derived here matches what that script creates.
    Files API name regex: ^[a-z](?!.*--)[a-z0-9\\-@.+_]{1,62}(?<!-)$
    """
    name = repo_id.lower().replace("/", "-")
    name = re.sub(r"[^a-z0-9\-@.+_]+", "-", name)
    name = re.sub(r"-{2,}", "-", name)
    name = name.strip("-")
    if not name:
        name = "migrated-fileset"
    if not name[0].isalpha():
        name = f"f-{name}"
    name = name[:63].rstrip("-")
    if "--" in name:
        name = re.sub(r"-{2,}", "-", name).rstrip("-")
    if not name:
        name = "migrated-fileset"
    return name


def _derive_fileset_ref(files_url: str, fallback_workspace: str) -> str | None:
    """Derive a V2 fileset reference (workspace/name) from a V1 artifact files_url.

    Expects URLs of the form hf://datasets/<namespace>/<repo>.  The workspace is
    taken from the repo namespace; the fileset name is sanitized via
    _sanitize_fileset_name so it matches what v2_migration.py would create.
    Returns None if the URL cannot be parsed.
    """
    if not files_url.startswith(_HF_DATASETS_PREFIX):
        return None
    repo_id = files_url[len(_HF_DATASETS_PREFIX) :].strip("/")
    if not repo_id:
        return None
    fileset_name = _sanitize_fileset_name(repo_id)
    workspace = repo_id.split("/", 1)[0] if "/" in repo_id else fallback_workspace
    return f"{workspace}/{fileset_name}"


def _normalize_entity_name(name: str) -> str:
    """Replace characters invalid in a V2 model entity name with '-'.

    V2 allows [a-zA-Z0-9_.-]; everything else (e.g. '@') becomes '-'.
    Consecutive hyphens are collapsed and leading/trailing hyphens stripped.
    """
    normalized = re.sub(r"[^a-zA-Z0-9_.\-]", "-", name)
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized.strip("-")


def _plan_model_entity(
    v1_client: NeMoMicroservices,
    v1_entity_id: str,
    default_namespace: str,
    target_workspace: str | None,
) -> ModelEntityPlan:
    """Fetch a V1 model entity and produce a ModelEntityPlan for V2."""
    if "/" in v1_entity_id:
        v1_namespace, v1_name = v1_entity_id.split("/", 1)
    else:
        v1_namespace, v1_name = default_namespace, v1_entity_id

    v2_workspace = target_workspace or v1_namespace
    v2_name = _normalize_entity_name(v1_name)

    try:
        m = v1_client.models.retrieve(v1_name, namespace=v1_namespace)
    except Exception as exc:
        return ModelEntityPlan(
            v1_namespace=v1_namespace,
            v1_name=v1_name,
            v2_workspace=v2_workspace,
            v2_name=v2_name,
            description=None,
            spec=None,
            base_model=None,
            finetuning_type=None,
            fileset=None,
            files_repo_id=None,
            api_endpoint=None,
            custom_fields=None,
            model_providers=None,
            ownership=None,
            project=None,
            prompt=None,
            skipped=True,
            skip_reason=f"could not retrieve V1 model entity: {exc}",
        )

    warnings: list[str] = []

    # peft → finetuning_type
    finetuning_type: str | None = None
    peft = getattr(m, "peft", None)
    if peft is not None:
        ft = getattr(peft, "finetuning_type", None)
        if ft is not None:
            finetuning_type = str(ft)
        if getattr(peft, "lora", None) is not None or getattr(peft, "p_tuning", None) is not None:
            warnings.append(
                "V1 peft.lora/p_tuning adapter config was not migrated. "
                "Re-attach adapters via the V2 Models API after migration."
            )

    fileset: str | None = None
    files_repo_id: str | None = None
    artifact = getattr(m, "artifact", None)
    if artifact is not None:
        files_url = getattr(artifact, "files_url", None) or ""
        fileset = _derive_fileset_ref(files_url, v2_workspace) if files_url else None
        if fileset:
            # Extract the raw repo_id (strip the hf://datasets/ prefix).
            repo_id = (
                files_url[len(_HF_DATASETS_PREFIX) :].strip("/") if files_url.startswith(_HF_DATASETS_PREFIX) else None
            )
            files_repo_id = repo_id or None
            warnings.append(
                f"V1 artifact.files_url='{files_url}' mapped to V2 fileset '{fileset}'. "
                "Run the files migration script first to ensure the fileset exists."
            )
        else:
            warnings.append(
                f"V1 artifact.files_url='{files_url}' could not be mapped to a V2 fileset "
                "(unexpected URL format). Register the fileset manually."
            )

    def _to_dict(obj: Any) -> dict[str, Any] | None:
        if obj is None:
            return None
        if isinstance(obj, dict):
            return obj
        try:
            return obj.model_dump(exclude_none=True)
        except Exception:
            return None

    return ModelEntityPlan(
        v1_namespace=v1_namespace,
        v1_name=v1_name,
        v2_workspace=v2_workspace,
        v2_name=v2_name,
        description=getattr(m, "description", None) or None,
        spec=_to_dict(getattr(m, "spec", None)),
        base_model=getattr(m, "base_model", None) or None,
        finetuning_type=finetuning_type,
        fileset=fileset,
        files_repo_id=files_repo_id,
        api_endpoint=_to_dict(getattr(m, "api_endpoint", None)),
        custom_fields=_to_dict(getattr(m, "custom_fields", None)),
        model_providers=list(m.model_providers) if getattr(m, "model_providers", None) else None,
        ownership=_to_dict(getattr(m, "ownership", None)),
        project=getattr(m, "project", None) or None,
        prompt=_to_dict(getattr(m, "prompt", None)),
        skipped=False,
        skip_reason=None,
        warnings=warnings,
    )


def _plan_config(
    v1_config: Any,
    target_workspace: str | None,
    *,
    name_override: str | None = None,
    namespace_override: str | None = None,
) -> ConfigPlan:
    """Translate a V1 DeploymentConfig into a ConfigPlan."""
    warnings: list[str] = []
    v1_namespace = namespace_override or getattr(v1_config, "namespace", None) or ""
    v1_config_name = name_override or getattr(v1_config, "name", None) or ""
    v2_workspace, v2_config_name = _resolve_v2_names(v1_namespace, v1_config_name, target_workspace)

    # External-endpoint-only configs have no NIM deployment and cannot be migrated as
    # V2 deployments. They should be registered via the inference gateway instead.
    v1_nim = getattr(v1_config, "nim_deployment", None)
    if v1_nim is None:
        external = getattr(v1_config, "external_endpoint", None)
        skip_reason = (
            "Config has no nim_deployment (external_endpoint only). Register via inference gateway in V2."
            if external
            else "Config has no nim_deployment."
        )
        return ConfigPlan(
            v1_namespace=v1_namespace,
            v1_config_name=v1_config_name,
            v2_workspace=v2_workspace,
            v2_config_name=v2_config_name,
            nim_deployment=None,
            model_entity_id=None,
            description=getattr(v1_config, "description", None),
            project=getattr(v1_config, "project", None),
            skipped=True,
            skip_reason=skip_reason,
        )

    if getattr(v1_config, "external_endpoint", None):
        warnings.append(
            "Config also has an external_endpoint which has no V2 equivalent; "
            "only the nim_deployment portion is migrated. "
            "Register the external endpoint via inference gateway."
        )

    nim_plan = _translate_nim_deployment(v1_nim, warnings)
    model_entity_id = _extract_model_entity_id(getattr(v1_config, "model", None))

    return ConfigPlan(
        v1_namespace=v1_namespace,
        v1_config_name=v1_config_name,
        v2_workspace=v2_workspace,
        v2_config_name=v2_config_name,
        nim_deployment=nim_plan,
        model_entity_id=model_entity_id,
        description=getattr(v1_config, "description", None),
        project=getattr(v1_config, "project", None),
        skipped=False,
        skip_reason=None,
        warnings=warnings,
    )


def _fetch_all_pages(list_fn: Any, **kwargs: Any) -> list[Any]:
    """Exhaust a paginated V1 list endpoint and return all items."""
    items: list[Any] = []
    page = 1
    while True:
        page_result = list_fn(page=page, page_size=100, **kwargs)
        batch = list(page_result)
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return items


def _resolve_deployment_config(deployment: Any, v1_client: NeMoMicroservices) -> Any | None:
    """Return the DeploymentConfig for a deployment, fetching from the API if needed."""
    config_field = getattr(deployment, "config", None)
    if config_field is None:
        return None
    # Already an embedded DeploymentConfig object.
    if not isinstance(config_field, str):
        return config_field
    # String reference: parse as "namespace/config_name" or just "config_name".
    config_ref = config_field
    dep_namespace = getattr(deployment, "namespace", None) or ""
    if "/" in config_ref:
        ref_ns, ref_name = config_ref.split("/", 1)
    else:
        ref_ns, ref_name = dep_namespace, config_ref
    if not ref_name:
        logger.warning("Deployment %s/%s has empty config reference.", dep_namespace, deployment.name)
        return None
    try:
        return v1_client.deployment.configs.retrieve(ref_name, namespace=ref_ns)
    except Exception as exc:
        logger.warning(
            "Could not fetch config '%s/%s' for deployment '%s/%s': %s",
            ref_ns,
            ref_name,
            dep_namespace,
            getattr(deployment, "name", "?"),
            exc,
        )
        return None


def create_plan(
    cfg: RuntimeConfig,
    *,
    namespaces: list[str],
    namespace_prefix: str | None,
) -> dict[str, Any]:
    v1_client = _get_v1_client(cfg)
    v2_sdk = _get_v2_sdk(cfg)
    resolved_v2_endpoint = str(v2_sdk.base_url)

    # Fetch all V1 deployments in one pass, then filter by namespace / prefix / status.
    logger.info("Fetching all V1 model deployments...")
    all_deployments = _fetch_all_pages(v1_client.deployment.model_deployments.list)
    logger.info("Found %d total V1 deployments.", len(all_deployments))

    def _matches_scope(dep: Any) -> bool:
        ns = getattr(dep, "namespace", None) or ""
        if namespaces:
            return ns in namespaces
        if namespace_prefix:
            return ns.startswith(namespace_prefix)
        return True

    def _is_ready(dep: Any) -> bool:
        status_details = getattr(dep, "status_details", None)
        if status_details is None:
            return False
        status = getattr(status_details, "status", None)
        return str(status).upper() == _READY_STATUS

    scoped = [d for d in all_deployments if _matches_scope(d)]
    ready = [d for d in scoped if _is_ready(d)]
    skipped_not_ready = len(scoped) - len(ready)

    logger.info(
        "Scoped to %d deployments (%d READY, %d skipped non-READY).",
        len(scoped),
        len(ready),
        skipped_not_ready,
    )

    # Build the set of unique configs needed, keyed by (namespace, config_ref).
    # We de-duplicate so each V1 config is translated only once.
    config_plans: dict[str, ConfigPlan] = {}  # key: "v1_namespace/v1_config_name"
    deployment_plans: list[DeploymentPlan] = []
    skipped_deployments: list[dict[str, str]] = []

    for dep in ready:
        dep_namespace = getattr(dep, "namespace", None) or ""
        dep_name = getattr(dep, "name", None) or ""
        dep_status = str(getattr(getattr(dep, "status_details", None), "status", "?"))

        v1_config = _resolve_deployment_config(dep, v1_client)
        if v1_config is None:
            logger.warning("Skipping deployment %s/%s: could not resolve config.", dep_namespace, dep_name)
            skipped_deployments.append(
                {
                    "namespace": dep_namespace,
                    "name": dep_name,
                    "reason": "could not resolve deployment config",
                }
            )
            continue

        v1_config_name = getattr(v1_config, "name", None) or ""
        v1_config_ns = getattr(v1_config, "namespace", None) or dep_namespace
        if not v1_config_name:
            # Inline/anonymous config — no name on the config object itself.
            # Synthesize a name from the deployment so it can still be migrated.
            v1_config_name = dep_name
            logger.debug(
                "Deployment %s/%s has an inline config with no name; using deployment name '%s' as config name.",
                dep_namespace,
                dep_name,
                dep_name,
            )
        config_key = f"{v1_config_ns}/{v1_config_name}"

        if config_key not in config_plans:
            config_plans[config_key] = _plan_config(
                v1_config,
                cfg.target_workspace,
                name_override=v1_config_name,
                namespace_override=v1_config_ns,
            )

        cp = config_plans[config_key]
        if cp.skipped:
            logger.warning(
                "Skipping deployment %s/%s: its config was skipped (%s).",
                dep_namespace,
                dep_name,
                cp.skip_reason,
            )
            skipped_deployments.append(
                {
                    "namespace": dep_namespace,
                    "name": dep_name,
                    "reason": f"config skipped: {cp.skip_reason}",
                }
            )
            continue

        dep_warnings: list[str] = []
        if getattr(dep, "async_enabled", None):
            dep_warnings.append("V1 async_enabled=True has no V2 equivalent and was dropped.")
        if getattr(dep, "models", None):
            dep_warnings.append(
                f"V1 models={dep.models!r} is informational only; "
                "model association in V2 is handled via the deployment config's model_entity_id."
            )

        v2_workspace, v2_dep_name = _resolve_v2_names(dep_namespace, dep_name, cfg.target_workspace)
        deployment_plans.append(
            DeploymentPlan(
                v1_namespace=dep_namespace,
                v1_deployment_name=dep_name,
                v1_status=dep_status,
                v2_workspace=v2_workspace,
                v2_deployment_name=v2_dep_name,
                v2_config_name=cp.v2_config_name,
                project=getattr(dep, "project", None),
                warnings=dep_warnings,
            )
        )

    all_config_plans = list(config_plans.values())
    active_configs = [cp for cp in all_config_plans if not cp.skipped]
    skipped_configs = [cp for cp in all_config_plans if cp.skipped]

    # Collect the unique model entity IDs referenced by active configs and plan their migration.
    entity_id_to_plan: dict[str, ModelEntityPlan] = {}
    for cp in active_configs:
        eid = cp.model_entity_id
        if eid and eid not in entity_id_to_plan:
            logger.info("Planning model entity migration for '%s'...", eid)
            entity_id_to_plan[eid] = _plan_model_entity(v1_client, eid, cp.v1_namespace, cfg.target_workspace)

    all_entity_plans = list(entity_id_to_plan.values())
    active_entities = [ep for ep in all_entity_plans if not ep.skipped]
    skipped_entities = [ep for ep in all_entity_plans if ep.skipped]

    # Collect deduplicated HF repo_ids needed for the files migration pre-step.
    files_repos_needed: list[str] = sorted({ep.files_repo_id for ep in active_entities if ep.files_repo_id})

    return {
        "generated_at": _now_iso(),
        "source": {
            "type": "v1_deployment_management",
            "endpoint": cfg.v1_base_url,
        },
        "target": {
            "type": "v2_inference_deployments",
            "endpoint": resolved_v2_endpoint,
            "workspace": cfg.target_workspace or "inferred_from_v1_namespace",
        },
        "summary": {
            "deployment_count": len(deployment_plans),
            "config_count": len(active_configs),
            "model_entity_count": len(active_entities),
            "skipped_deployment_count": len(skipped_deployments) + skipped_not_ready,
            "skipped_config_count": len(skipped_configs),
            "skipped_model_entity_count": len(skipped_entities),
        },
        "files_repos_needed": files_repos_needed,
        "model_entities": [asdict(ep) for ep in active_entities],
        "configs": [asdict(cp) for cp in active_configs],
        "deployments": [asdict(dp) for dp in deployment_plans],
        "skipped_model_entities": [asdict(ep) for ep in skipped_entities],
        "skipped_configs": [asdict(cp) for cp in skipped_configs],
        "skipped_deployments": skipped_deployments,
    }


def _ensure_model_entity(
    sdk: NeMoPlatform,
    ep: dict[str, Any],
    dry_run: bool,
) -> Literal["dry_run", "exists", "created"]:
    workspace = str(ep["v2_workspace"])
    name = str(ep["v2_name"])
    if dry_run:
        return "dry_run"
    try:
        sdk.models.retrieve(name, workspace=workspace)
        return "exists"
    except NotFoundError:
        create_kwargs: dict[str, Any] = {}
        for field_name in ("description", "base_model", "finetuning_type", "project"):
            if ep.get(field_name):
                create_kwargs[field_name] = ep[field_name]
        for field_name in ("spec", "api_endpoint", "custom_fields", "model_providers", "ownership", "prompt"):
            if ep.get(field_name):
                create_kwargs[field_name] = ep[field_name]

        # Attach fileset if it exists in V2 (requires files migration to have run first).
        fileset_ref: str | None = ep.get("fileset")
        if fileset_ref and "/" in fileset_ref:
            fs_workspace, fs_name = fileset_ref.split("/", 1)
            try:
                sdk.files.filesets.retrieve(name=fs_name, workspace=fs_workspace)
                create_kwargs["fileset"] = fileset_ref
                logger.info("Attaching fileset '%s' to model entity '%s/%s'.", fileset_ref, workspace, name)
            except NotFoundError:
                logger.warning(
                    "Fileset '%s' not found in V2; skipping fileset attachment for model entity '%s/%s'. "
                    "Run the files migration script first, then update the entity.",
                    fileset_ref,
                    workspace,
                    name,
                )
            except Exception as exc:
                logger.warning(
                    "Could not verify fileset '%s': %s. Skipping fileset attachment for '%s/%s'.",
                    fileset_ref,
                    exc,
                    workspace,
                    name,
                )

        sdk.models.create(name=name, workspace=workspace, **create_kwargs)
        return "created"


def _ensure_workspace(sdk: NeMoPlatform, workspace: str, dry_run: bool) -> Literal["dry_run", "exists", "created"]:
    if dry_run:
        return "dry_run"
    try:
        sdk.workspaces.retrieve(workspace)
        return "exists"
    except NotFoundError:
        try:
            sdk.workspaces.create(name=workspace)
        except ConflictError:
            return "exists"
        return "created"


def _ensure_deployment_config(
    sdk: NeMoPlatform,
    workspace: str,
    cp: dict[str, Any],
    dry_run: bool,
    *,
    entity_id_map: dict[str, str] | None = None,
) -> Literal["dry_run", "exists", "created"]:
    name = str(cp["v2_config_name"])
    if dry_run:
        return "dry_run"
    try:
        sdk.inference.deployment_configs.retrieve(name, workspace=workspace)
        return "exists"
    except NotFoundError:
        nim = cp["nim_deployment"]
        nim_param: dict[str, Any] = {"gpu": nim["gpu"]}
        for src, dst in [
            ("image_name", "image_name"),
            ("image_tag", "image_tag"),
            ("disk_size", "disk_size"),
            ("lora_enabled", "lora_enabled"),
            ("additional_envs", "additional_envs"),
        ]:
            if nim.get(src) is not None:
                nim_param[dst] = nim[src]

        create_kwargs: dict[str, Any] = {"nim_deployment": nim_param}
        if cp.get("description"):
            create_kwargs["description"] = cp["description"]
        if cp.get("model_entity_id"):
            v1_eid = cp["model_entity_id"]
            # Use the normalized V2 entity ID if we migrated it, otherwise fall back to V1 value.
            create_kwargs["model_entity_id"] = (entity_id_map or {}).get(v1_eid, v1_eid)
        if cp.get("project"):
            create_kwargs["project"] = cp["project"]

        sdk.inference.deployment_configs.create(name=name, workspace=workspace, **create_kwargs)
        return "created"


def _ensure_deployment(
    sdk: NeMoPlatform,
    workspace: str,
    dp: dict[str, Any],
    dry_run: bool,
) -> Literal["dry_run", "exists", "created"]:
    name = str(dp["v2_deployment_name"])
    config = str(dp["v2_config_name"])
    if dry_run:
        return "dry_run"
    try:
        sdk.inference.deployments.retrieve(name, workspace=workspace)
        return "exists"
    except NotFoundError:
        create_kwargs: dict[str, Any] = {}
        if dp.get("project"):
            create_kwargs["project"] = dp["project"]
        sdk.inference.deployments.create(
            name=name,
            config=config,
            workspace=workspace,
            **create_kwargs,
        )
        return "created"


def apply_plan(
    cfg: RuntimeConfig,
    plan: dict[str, Any],
    *,
    dry_run: bool,
    max_deployments: int | None,
) -> dict[str, Any]:
    sdk = _get_v2_sdk(cfg)

    # --- Model entities (must exist before configs reference them) ---
    entity_results: dict[str, str] = {}
    # Build V1 entity_id → V2 "workspace/name" mapping for use in config creation.
    entity_id_map: dict[str, str] = {}
    for ep in plan.get("model_entities", []):
        v1_id = f"{ep['v1_namespace']}/{ep['v1_name']}" if ep.get("v1_namespace") else ep["v1_name"]
        v2_id = f"{ep['v2_workspace']}/{ep['v2_name']}"
        entity_id_map[v1_id] = v2_id
        try:
            entity_results[v1_id] = _ensure_model_entity(sdk, ep, dry_run=dry_run)
        except Exception as exc:
            entity_results[v1_id] = f"failed: {exc}"
            logger.error("Failed to ensure model entity '%s': %s", v1_id, exc)

    # Index configs by "workspace/config_name" to avoid collisions across workspaces.
    config_index: dict[str, dict[str, Any]] = {
        f"{cp['v2_workspace']}/{cp['v2_config_name']}": cp for cp in plan.get("configs", [])
    }
    deployment_entries: list[dict[str, Any]] = list(plan.get("deployments", []))
    if max_deployments is not None:
        deployment_entries = deployment_entries[:max_deployments]

    # Collect workspaces needed.
    workspaces_needed: set[str] = {dp["v2_workspace"] for dp in deployment_entries}
    workspace_statuses: dict[str, str] = {}
    for ws in sorted(workspaces_needed):
        try:
            workspace_statuses[ws] = _ensure_workspace(sdk, ws, dry_run=dry_run)
        except Exception as exc:
            workspace_statuses[ws] = f"failed: {exc}"
            logger.error("Failed to ensure workspace '%s': %s", ws, exc)

    # Configs for the workspaces we're about to deploy into (keyed by workspace/name).
    configs_needed: set[str] = {f"{dp['v2_workspace']}/{dp['v2_config_name']}" for dp in deployment_entries}
    config_results: dict[str, str] = {}
    for config_key in sorted(configs_needed):
        cp = config_index.get(config_key)
        if cp is None:
            config_results[config_key] = "missing_from_plan"
            logger.error("Config '%s' referenced by a deployment is not in the plan.", config_key)
            continue
        ws = cp["v2_workspace"]
        if workspace_statuses.get(ws, "").startswith("failed"):
            config_results[config_key] = "skipped: workspace failed"
            continue
        try:
            config_results[config_key] = _ensure_deployment_config(
                sdk, ws, cp, dry_run=dry_run, entity_id_map=entity_id_map
            )
        except Exception as exc:
            config_results[config_key] = f"failed: {exc}"
            logger.error("Failed to ensure deployment config '%s' in workspace '%s': %s", config_key, ws, exc)

    # Now create deployments.
    deployment_results: list[dict[str, Any]] = []
    created = 0
    skipped = 0
    failed = 0

    for dp in deployment_entries:
        ws = dp["v2_workspace"]
        config_name = dp["v2_config_name"]
        dep_name = dp["v2_deployment_name"]
        config_key = f"{ws}/{config_name}"

        result: dict[str, Any] = {
            "v1_namespace": dp["v1_namespace"],
            "v1_deployment_name": dp["v1_deployment_name"],
            "v2_workspace": ws,
            "v2_deployment_name": dep_name,
            "v2_config_name": config_name,
            "workspace_status": workspace_statuses.get(ws, "unknown"),
            "config_status": config_results.get(config_key, "unknown"),
            "deployment_status": "unknown",
        }

        if workspace_statuses.get(ws, "").startswith("failed"):
            result["deployment_status"] = "skipped: workspace failed"
            skipped += 1
            deployment_results.append(result)
            continue

        if (
            config_results.get(config_key, "").startswith("failed")
            or config_results.get(config_key) == "missing_from_plan"
        ):
            result["deployment_status"] = f"skipped: config failed ({config_results.get(config_key)})"
            skipped += 1
            deployment_results.append(result)
            continue

        try:
            status = _ensure_deployment(sdk, ws, dp, dry_run=dry_run)
            result["deployment_status"] = status
            if status in ("created", "dry_run"):
                created += 1
            else:
                skipped += 1
        except Exception as exc:
            result["deployment_status"] = f"failed: {exc}"
            failed += 1
            logger.error("Failed to create deployment '%s' in workspace '%s': %s", dep_name, ws, exc)

        deployment_results.append(result)

    entity_created = sum(1 for s in entity_results.values() if s in ("created", "dry_run"))
    entity_failed = sum(1 for s in entity_results.values() if str(s).startswith("failed"))

    return {
        "applied_at": _now_iso(),
        "dry_run": dry_run,
        "summary": {
            "model_entity_count": len(entity_results),
            "created_model_entities": entity_created,
            "failed_model_entities": entity_failed,
            "deployment_count": len(deployment_results),
            "created_deployments": created,
            "skipped_deployments": skipped,
            "failed_deployments": failed,
        },
        "model_entity_statuses": entity_results,
        "workspace_statuses": workspace_statuses,
        "config_statuses": config_results,
        "deployments": deployment_results,
    }


def _normalize_model_name(name: str) -> str:
    """Normalize a model name to V2's DNS-label requirements.

    V2 requires names to start with a lowercase letter, be 2-63 characters,
    and contain only lowercase letters, digits, and hyphens.  V1 namespaces
    and model names often contain underscores, so we replace them with hyphens
    as a best-effort normalization.
    """
    return name.replace("_", "-").lower()


def _flatten_model_id(model_entity_id: str) -> str:
    """Flatten a namespaced V1 model ID to V2's system-workspace naming convention.

    V2 stores models as 'system/{namespace}-{name}' with dots and slashes
    replaced by hyphens, e.g. 'meta/llama-3.3-70b-instruct' →
    'meta-llama-3-3-70b-instruct' (matched against the local part of a
    'system/...' entry).
    """
    return model_entity_id.replace("/", "-").replace(".", "-").replace("_", "-").lower()


def _match_model_id(
    dep_name: str,
    model_entity_id: str | None,
    available: list[str],
) -> str | None:
    """Return the best matching model ID from the gateway's available list.

    Matching order (first match wins):
    1. Exact match on model_entity_id
    2. Normalized match on model_entity_id (underscores → hyphens)
    3. Flattened match: 'ns/name' → 'ns-name' (V2 system-workspace convention)
    4. Local-name-only matches (with and without normalization)
    5. Same for dep_name
    """
    if not available:
        return None

    candidates: list[str | None] = [model_entity_id]
    if model_entity_id:
        candidates.append(_normalize_model_name(model_entity_id))
        candidates.append(_flatten_model_id(model_entity_id))
        entity_local = model_entity_id.split("/", 1)[-1]
        candidates += [entity_local, _normalize_model_name(entity_local)]

    dep_local = dep_name.split("/", 1)[-1]
    candidates += [dep_local, _normalize_model_name(dep_local)]

    available_by_local = {mid.split("/", 1)[-1]: mid for mid in available}

    for candidate in candidates:
        if not candidate:
            continue
        if candidate in available:
            return candidate
        if candidate in available_by_local:
            return available_by_local[candidate]

    return None


def verify_deployments(
    cfg: RuntimeConfig,
    plan: dict[str, Any],
    *,
    timeout: float,
    max_deployments: int | None,
) -> dict[str, Any]:
    sdk = _get_v2_sdk(cfg)

    config_index: dict[str, dict[str, Any]] = {
        f"{cp['v2_workspace']}/{cp['v2_config_name']}": cp for cp in plan.get("configs", [])
    }
    deployment_entries: list[dict[str, Any]] = list(plan.get("deployments", []))
    if max_deployments is not None:
        deployment_entries = deployment_entries[:max_deployments]

    # Cache the gateway model list per workspace to avoid redundant calls.
    workspace_models: dict[str, list[str]] = {}

    def _list_workspace_models(ws: str) -> list[str]:
        if ws not in workspace_models:
            try:
                resp = sdk.inference.gateway.openai.v1.models.list(workspace=ws)
                workspace_models[ws] = [m.id for m in resp.data if m.id]
                logger.debug("Gateway models for workspace '%s': %s", ws, workspace_models[ws])
            except Exception as exc:
                logger.warning("Could not list models for workspace '%s': %s", ws, exc)
                workspace_models[ws] = []
        return workspace_models[ws]

    results: list[dict[str, Any]] = []
    passed = 0
    failed = 0
    skipped = 0

    for dp in deployment_entries:
        ws = dp["v2_workspace"]
        dep_name = dp["v2_deployment_name"]
        config_key = f"{ws}/{dp['v2_config_name']}"
        cp = config_index.get(config_key)
        model_entity_id: str | None = cp.get("model_entity_id") if cp else None

        result: dict[str, Any] = {
            "v2_workspace": ws,
            "v2_deployment_name": dep_name,
            "model_entity_id": model_entity_id,
            "status": "unknown",
        }

        available = _list_workspace_models(ws)
        model_id = _match_model_id(dep_name, model_entity_id, available)

        if model_id is None:
            available_str = ", ".join(available) if available else "none"
            result["status"] = f"skipped: no matching model in gateway (available: {available_str})"
            skipped += 1
            results.append(result)
            continue

        # The matched model may live in a different workspace (e.g. "system/...").
        # Use the workspace embedded in the model ID for the completion request.
        inference_ws = model_id.split("/", 1)[0] if "/" in model_id else ws
        result["model_id_used"] = model_id
        result["inference_workspace"] = inference_ws
        try:
            resp = sdk.inference.gateway.openai.post(
                "v1/chat/completions",
                workspace=inference_ws,
                body={
                    "model": model_id,
                    "messages": [{"role": "user", "content": "say hello"}],
                    "max_tokens": 10,
                },
                timeout=timeout,
            )
            result["status"] = "ok"
            resp_dict: dict[str, Any] = resp if isinstance(resp, dict) else {}
            choices: list[Any] = resp_dict.get("choices") or []  # type: ignore[assignment]
            if choices:
                content = (choices[0].get("message") or {}).get("content") or ""
                result["response_snippet"] = str(content)[:120]
            passed += 1
            logger.info(
                "Inference check OK for deployment '%s/%s' (model: %s, inference_ws: %s).",
                ws,
                dep_name,
                model_id,
                inference_ws,
            )
        except Exception as exc:
            result["status"] = f"failed: {exc}"
            failed += 1
            logger.error("Inference check FAILED for deployment '%s/%s': %s", ws, dep_name, exc)

        results.append(result)

    return {
        "verified_at": _now_iso(),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "deployments": results,
    }


def run_setup(args: argparse.Namespace) -> int:
    cfg = _resolve_runtime_config(args)
    v2_mode = "explicit base URL/env" if cfg.v2_base_url else "nemo CLI context/config"
    print("Resolved configuration:")
    print(f"  v1_base_url:      {cfg.v1_base_url}")
    print(f"  v1_api_key:       {'set' if cfg.v1_api_key else 'not set'}")
    print(f"  v2_base_url:      {cfg.v2_base_url or '<from nemo context>'}")
    print(f"  v2_auth_mode:     {v2_mode}")
    print(f"  target_workspace: {cfg.target_workspace or '<inferred from V1 namespace>'}")
    print("  auth_note: If auth is enabled on V2, run 'nemo auth login' before using this script.")

    if not args.check:
        return 0

    requested_namespaces: list[str] = list(getattr(args, "namespace", []) or [])
    requested_prefix: str | None = getattr(args, "namespace_prefix", None)

    print("\nRunning connectivity checks...")

    # V1 check.
    try:
        v1_client = _get_v1_client(cfg)
        if requested_namespaces:
            for ns in requested_namespaces:
                # Use a single-page list as a lightweight probe.
                result = v1_client.deployment.model_deployments.list(page=1, page_size=1)
                count = len(list(result))
                print(f"  V1 deployment service: OK (namespace={ns}, sample_count={count})")
        elif requested_prefix:
            result = v1_client.deployment.model_deployments.list(page=1, page_size=1)
            sample = next(iter(result), None)
            sample_name = (
                f"{getattr(sample, 'namespace', '?')}/{getattr(sample, 'name', '?')}" if sample else "<none visible>"
            )
            print(f"  V1 deployment service: OK (prefix={requested_prefix}, sample deployment: {sample_name})")
        else:
            result = v1_client.deployment.model_deployments.list(page=1, page_size=1)
            sample = next(iter(result), None)
            sample_name = (
                f"{getattr(sample, 'namespace', '?')}/{getattr(sample, 'name', '?')}" if sample else "<none visible>"
            )
            print(f"  V1 deployment service: OK (sample deployment: {sample_name})")
    except Exception as exc:
        print(f"  V1 deployment service: FAIL ({exc})")
        return 1

    # V2 check.
    try:
        v2_sdk = _get_v2_sdk(cfg)
        _ = next(iter(v2_sdk.workspaces.list(page_size=1)), None)
        print(f"  V2 inference service:  OK (resolved base_url: {v2_sdk.base_url})")
    except Exception as exc:
        print(f"  V2 inference service:  FAIL ({exc})")
        return 1

    return 0


def run_plan(args: argparse.Namespace) -> int:
    cfg = _resolve_runtime_config(args)
    namespaces: list[str] = args.namespace or []
    namespace_prefix: str | None = args.namespace_prefix

    if namespace_prefix is not None and not namespace_prefix.strip():
        raise ValueError("Invalid --namespace-prefix: cannot be empty.")

    plan = create_plan(cfg, namespaces=namespaces, namespace_prefix=namespace_prefix)
    output = Path(args.plan)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    summary = plan["summary"]
    print(f"Wrote plan: {output}")
    print(
        f"Summary: {summary['deployment_count']} deployments, "
        f"{summary['config_count']} configs, "
        f"{summary['model_entity_count']} model entities"
    )
    if summary["skipped_deployment_count"] > 0:
        print(f"Skipped deployments: {summary['skipped_deployment_count']}")
    if summary["skipped_config_count"] > 0:
        print(f"Skipped configs: {summary['skipped_config_count']} (external-endpoint-only or no NIM config)")
    if summary["skipped_model_entity_count"] > 0:
        print(f"Skipped model entities: {summary['skipped_model_entity_count']} (could not retrieve from V1)")
    return 0


def run_apply(args: argparse.Namespace) -> int:
    cfg = _resolve_runtime_config(args)
    plan_path = Path(args.plan)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    # Allow --target-workspace to override what was set at plan time.
    if args.target_workspace and args.target_workspace != cfg.target_workspace:
        logger.warning(
            "--target-workspace '%s' overrides plan-time workspace setting.",
            args.target_workspace,
        )
        cfg = RuntimeConfig(
            v1_base_url=cfg.v1_base_url,
            v1_api_key=cfg.v1_api_key,
            v2_base_url=cfg.v2_base_url,
            target_workspace=args.target_workspace,
        )

    result = apply_plan(
        cfg,
        plan,
        dry_run=args.dry_run,
        max_deployments=args.max_deployments,
    )

    result_path = Path(args.result_output)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    summary = result["summary"]
    print(f"Wrote apply result: {result_path}")
    print(f"Model entities: {summary['created_model_entities']} created, {summary['failed_model_entities']} failed")
    print(
        f"Deployments: {summary['created_deployments']} created, "
        f"{summary['skipped_deployments']} skipped, "
        f"{summary['failed_deployments']} failed"
    )
    return 0 if (summary["failed_deployments"] == 0 and summary["failed_model_entities"] == 0) else 1


def run_verify(args: argparse.Namespace) -> int:
    cfg = _resolve_runtime_config(args)
    plan_path = Path(args.plan)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    result = verify_deployments(
        cfg,
        plan,
        timeout=args.timeout,
        max_deployments=args.max_deployments,
    )

    result_path = Path(args.result_output)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    summary = result["summary"]
    print(f"Wrote verify result: {result_path}")
    print(f"Verify summary: {summary['passed']} passed, {summary['failed']} failed, {summary['skipped']} skipped")
    return 0 if summary["failed"] == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate V1 model deployments to V2")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--v1-base-url",
        default=None,
        help="V1 NeMo Platform base URL (or NMP_V1_BASE_URL / NMP_BASE_URL).",
    )
    common.add_argument(
        "--v1-api-key",
        default=None,
        help="V1 API key (or NMP_V1_API_KEY).",
    )
    common.add_argument(
        "--v2-base-url",
        default=None,
        help="V2 NeMo Platform base URL (or NMP_V2_BASE_URL / NEMO_MICROSERVICES_BASE_URL). "
        "If omitted, uses active nemo context/config.",
    )
    common.add_argument(
        "--target-workspace",
        default=None,
        help="Override: migrate all namespaces into this single V2 workspace "
        "(deployment and config names will be prefixed with '<v1-namespace>-'). "
        "If omitted, each V1 namespace maps to a V2 workspace of the same name.",
    )
    common.add_argument("--log-level", default="INFO", help="Log level (DEBUG, INFO, WARNING, ERROR)")

    sub = parser.add_subparsers(dest="command", required=True)

    p_setup = sub.add_parser(
        "setup",
        help="Validate runtime config and optional connectivity",
        parents=[common],
    )
    p_setup.add_argument("--check", action="store_true", help="Run connectivity checks against both services.")
    p_setup.add_argument(
        "--namespace",
        action="append",
        default=[],
        help="V1 namespace to check access for (repeatable).",
    )
    p_setup.add_argument(
        "--namespace-prefix",
        default=None,
        help="V1 namespace prefix to validate (e.g. 'org-' to scope to namespaces starting with 'org-').",
    )
    p_setup.set_defaults(func=run_setup)

    p_plan = sub.add_parser(
        "plan",
        help="Discover READY V1 deployments and generate migration plan JSON",
        parents=[common],
    )
    p_plan.add_argument(
        "--namespace",
        action="append",
        default=[],
        help="V1 namespace to include (repeatable). Mutually exclusive with --namespace-prefix. "
        "If neither --namespace nor --namespace-prefix is given, all namespaces are included.",
    )
    p_plan.add_argument(
        "--namespace-prefix",
        default=None,
        help="Include all V1 namespaces starting with this prefix. "
        "If neither --namespace nor --namespace-prefix is given, all namespaces are included.",
    )
    p_plan.add_argument(
        "--plan",
        default="./v2_deployment_migration_plan.json",
        help="Path to write plan JSON (default: ./v2_deployment_migration_plan.json)",
    )
    p_plan.set_defaults(func=run_plan)

    p_apply = sub.add_parser(
        "apply",
        help="Apply a migration plan: create V2 workspaces, deployment configs, and deployments",
        parents=[common],
    )
    p_apply.add_argument("--plan", required=True, help="Path to plan JSON generated by 'plan'.")
    p_apply.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without writing to the V2 service.",
    )
    p_apply.add_argument(
        "--max-deployments",
        type=int,
        default=None,
        help="Apply only the first N deployments from the plan.",
    )
    p_apply.add_argument(
        "--result-output",
        default="./v2_deployment_migration_apply_result.json",
        help="Path to output apply result JSON (default: ./v2_deployment_migration_apply_result.json)",
    )
    p_apply.set_defaults(func=run_apply)

    p_verify = sub.add_parser(
        "verify",
        help="Send a hello-world chat completion to each deployed model to confirm reachability",
        parents=[common],
    )
    p_verify.add_argument("--plan", required=True, help="Path to plan JSON generated by 'plan'.")
    p_verify.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Per-request inference timeout in seconds (default: 60).",
    )
    p_verify.add_argument(
        "--max-deployments",
        type=int,
        default=None,
        help="Verify only the first N deployments from the plan.",
    )
    p_verify.add_argument(
        "--result-output",
        default="./v2_deployment_migration_verify_result.json",
        help="Path to output verify result JSON (default: ./v2_deployment_migration_verify_result.json)",
    )
    p_verify.set_defaults(func=run_verify)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(levelname)s: %(message)s",
    )
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
