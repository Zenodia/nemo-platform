#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Build JSON datasets for AUT evaluation from agentic-use task prompts.

This script converts ``instruction.md`` files into a NAT-compatible JSON dataset
for ``nemo agents evaluate`` / ``nat eval``.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import tomllib
from pathlib import Path

TASKS_DIR = Path(__file__).resolve().parent


def resolve_tasks(patterns: list[str]) -> list[Path]:
    candidates = [
        d
        for d in TASKS_DIR.iterdir()
        if d.is_dir() and (d / "instruction.md").exists() and d.name != "example-test-template"
    ]
    if not patterns:
        return sorted(candidates, key=lambda p: p.name)

    selected: list[Path] = []
    all_names = {d.name for d in candidates}
    by_name = {d.name: d for d in candidates}
    for pattern in patterns:
        if "*" in pattern or "?" in pattern:
            selected.extend(sorted([d for d in candidates if fnmatch.fnmatch(d.name, pattern)], key=lambda p: p.name))
            continue
        if pattern not in all_names:
            raise ValueError(f"Unknown task {pattern!r}. Available: {sorted(all_names)}")
        selected.append(by_name[pattern])
    return selected


def _relative_to_tasks(path: Path) -> str:
    return path.relative_to(TASKS_DIR).as_posix()


def _load_task_toml(task_dir: Path) -> dict:
    task_toml = task_dir / "task.toml"
    if not task_toml.exists():
        return {}
    return tomllib.loads(task_toml.read_text())


def _read_manifest(manifest_path: Path) -> list[str]:
    if not manifest_path.is_absolute():
        manifest_path = (TASKS_DIR / manifest_path).resolve()
    if not manifest_path.exists():
        raise FileNotFoundError(f"Task manifest not found: {manifest_path}")

    patterns: list[str] = []
    for raw_line in manifest_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _build_task_contract(task_dir: Path) -> dict:
    task_cfg = _load_task_toml(task_dir)
    metadata = task_cfg.get("metadata", {}) if isinstance(task_cfg, dict) else {}
    env_cfg = task_cfg.get("environment", {}) if isinstance(task_cfg, dict) else {}
    agent_cfg = task_cfg.get("agent", {}) if isinstance(task_cfg, dict) else {}
    verifier_cfg = task_cfg.get("verifier", {}) if isinstance(task_cfg, dict) else {}

    setup_scripts = sorted([_relative_to_tasks(p) for p in (task_dir / "environment").glob("setup-*.py")])
    has_compose = (task_dir / "environment" / "docker-compose.yaml").exists()
    tags = metadata.get("tags", []) if isinstance(metadata, dict) else []
    has_gpu_tag = any(str(tag).lower() == "gpu" for tag in tags) if isinstance(tags, list) else False
    gpu_count = env_cfg.get("gpus", 0) if isinstance(env_cfg, dict) else 0
    requires_gpu = bool(has_gpu_tag or (isinstance(gpu_count, (int, float)) and gpu_count > 0))

    return {
        "task_name": task_dir.name,
        "inputs": {
            "instruction": _relative_to_tasks(task_dir / "instruction.md"),
            "task_toml": _relative_to_tasks(task_dir / "task.toml"),
            "workflow": _relative_to_tasks(task_dir / "workflow.yml") if (task_dir / "workflow.yml").exists() else None,
            "environment_dockerfile": _relative_to_tasks(task_dir / "environment" / "Dockerfile"),
            "environment_setup_scripts": setup_scripts,
        },
        "correctness_oracle": {
            "pytest_file": _relative_to_tasks(task_dir / "tests" / "test_outputs.py"),
        },
        "task_metadata": {
            "difficulty": metadata.get("difficulty") if isinstance(metadata, dict) else None,
            "category": metadata.get("category") if isinstance(metadata, dict) else None,
            "tags": tags if isinstance(tags, list) else [],
        },
        "runtime_requirements": {
            "requires_docker_compose": has_compose,
            "requires_gpu": requires_gpu,
            "requires_docker_socket": has_compose,
            "allow_internet": env_cfg.get("allow_internet") if isinstance(env_cfg, dict) else None,
        },
        "timeouts_sec": {
            "agent": agent_cfg.get("timeout_sec") if isinstance(agent_cfg, dict) else None,
            "verifier": verifier_cfg.get("timeout_sec") if isinstance(verifier_cfg, dict) else None,
            "build": env_cfg.get("build_timeout_sec") if isinstance(env_cfg, dict) else None,
        },
    }


def build_rows(tasks: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for task_dir in tasks:
        instruction = (task_dir / "instruction.md").read_text().strip()
        contract = _build_task_contract(task_dir)
        rows.append(
            {
                "id": task_dir.name,
                "task_name": task_dir.name,
                "input_obj": instruction,
                # This row is consumed by runtime evaluators; correctness is still
                # determined by task-specific pytest verification in nat_runner.py.
                "expected_output_obj": "",
                "expected_trajectory": [],
                "full_dataset_entry": contract,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Build AUT eval dataset from tests/agentic-use tasks.")
    parser.add_argument("tasks", nargs="*", metavar="TASK_OR_GLOB", help="Task names or glob patterns.")
    parser.add_argument("--all", action="store_true", help="Include all tasks.")
    parser.add_argument(
        "--manifest",
        type=Path,
        help=("Task manifest file with one task/glob per line. Relative paths resolve from tests/agentic-use/."),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=TASKS_DIR / "aut-eval-data.json",
        help="Output dataset path (default: tests/agentic-use/aut-eval-data.json)",
    )
    args = parser.parse_args()

    if args.all and args.manifest is not None:
        raise ValueError("--all and --manifest are mutually exclusive")
    if args.tasks and args.manifest is not None:
        raise ValueError("Positional TASK_OR_GLOB args and --manifest are mutually exclusive")
    if args.tasks and args.all:
        raise ValueError("Positional TASK_OR_GLOB args and --all are mutually exclusive")

    if args.manifest is not None:
        task_patterns = _read_manifest(args.manifest)
    else:
        task_patterns = [] if args.all else args.tasks

    tasks = resolve_tasks(task_patterns)
    rows = build_rows(tasks)
    payload = rows

    args.output.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
