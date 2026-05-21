# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for task-local Evaluator benchmark metrics."""

import importlib.util
from pathlib import Path
from types import ModuleType

from evaluator_agent_eval.artifacts import AgentArtifacts
from evaluator_agent_eval.factory import build_evaluator_scoring_row, capture_agent_attempt
from evaluator_agent_eval.runner import score_evaluator_rows
from evaluator_agent_eval.schemas import CapturedAgentAttempt
from evaluator_agent_eval.task_config import AgenticUseTaskConfig, load_agentic_use_task_config
from nemo_evaluator_sdk.metrics.base import Metric


def _load_task_metrics(task_name: str) -> ModuleType:
    agentic_use_dir = Path(__file__).parents[2]
    path = agentic_use_dir / task_name / "tests" / "task_metrics.py"
    spec = importlib.util.spec_from_file_location(f"{task_name}_task_metrics", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not import task metrics from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_surface_discovery_metric_normalizes_required_term_success(evaluator_task_dir: Path, agent_log_dir: Path):
    (agent_log_dir / "final_message.txt").write_text(
        """
Use packages/nemo_evaluator_sdk with Evaluator, ExactMatchMetric, and run_sync.

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path("packages/nemo_evaluator_sdk/src").resolve()))

from nemo_evaluator_sdk import Evaluator, ExactMatchMetric

rows = [
    {"question": "2+2?", "expected": "4", "prediction": "4"},
    {"question": "Capital of France?", "expected": "Paris", "prediction": "Lyon"},
]

result = Evaluator().run_sync(
    metrics=ExactMatchMetric(
        reference="{{item.expected}}",
        candidate="{{item.prediction}}",
    ),
    dataset=rows,
)
```
""".strip(),
        encoding="utf-8",
    )
    artifacts = AgentArtifacts.from_dir(agent_log_dir)
    task_config = load_agentic_use_task_config(evaluator_task_dir)
    attempt = capture_agent_attempt(task_dir=evaluator_task_dir, artifacts=artifacts)
    module = _load_task_metrics("evaluator-standalone-sdk-surface-discovery")

    scores = _score_task_metric(
        metric=module.SurfaceDiscoveryMetric(),
        task_dir=evaluator_task_dir,
        artifacts=artifacts,
        task_config=task_config,
        attempt=attempt,
    )

    assert scores["task_success"] == [1.0]
    assert scores["verification_score"] == [1.0]
    assert scores["output_schema_valid"] == [1.0]


def test_surface_discovery_metric_accepts_async_invocation(evaluator_task_dir: Path, agent_log_dir: Path):
    (agent_log_dir / "final_message.txt").write_text(
        """
Use packages/nemo_evaluator_sdk with Evaluator, ExactMatchMetric, and run.

```python
from pathlib import Path
import asyncio
import sys

sys.path.insert(0, str(Path("packages/nemo_evaluator_sdk/src").resolve()))

from nemo_evaluator_sdk import Evaluator, ExactMatchMetric

rows = [
    {"question": "2+2?", "expected": "4", "prediction": "4"},
    {"question": "Capital of France?", "expected": "Paris", "prediction": "Lyon"},
]

async def main() -> None:
    result = await Evaluator().run(
        metrics=ExactMatchMetric(
            reference="{{item.expected}}",
            candidate="{{item.prediction}}",
        ),
        dataset=rows,
    )
    print(result)

asyncio.run(main())
```
""".strip(),
        encoding="utf-8",
    )
    artifacts = AgentArtifacts.from_dir(agent_log_dir)
    task_config = load_agentic_use_task_config(evaluator_task_dir)
    attempt = capture_agent_attempt(task_dir=evaluator_task_dir, artifacts=artifacts)
    module = _load_task_metrics("evaluator-standalone-sdk-surface-discovery")

    scores = _score_task_metric(
        metric=module.SurfaceDiscoveryMetric(),
        task_dir=evaluator_task_dir,
        artifacts=artifacts,
        task_config=task_config,
        attempt=attempt,
    )

    assert scores["task_success"] == [1.0]
    assert scores["verification_score"] == [1.0]
    assert scores["output_schema_valid"] == [1.0]


def test_surface_discovery_metric_selects_complete_snippet(evaluator_task_dir: Path, agent_log_dir: Path):
    (agent_log_dir / "final_message.txt").write_text(
        """
Use packages/nemo_evaluator_sdk with Evaluator, ExactMatchMetric, and run_sync.

```python
from nemo_evaluator_sdk import Evaluator, ExactMatchMetric
```

```python
from nemo_evaluator_sdk import Evaluator, ExactMatchMetric

rows = [
    {"question": "2+2?", "expected": "4", "prediction": "4"},
    {"question": "Capital of France?", "expected": "Paris", "prediction": "Lyon"},
]

result = Evaluator().run_sync(
    metrics=ExactMatchMetric(
        reference="{{item.expected}}",
        candidate="{{item.prediction}}",
    ),
    dataset=rows,
)
```
""".strip(),
        encoding="utf-8",
    )
    artifacts = AgentArtifacts.from_dir(agent_log_dir)
    task_config = load_agentic_use_task_config(evaluator_task_dir)
    attempt = capture_agent_attempt(task_dir=evaluator_task_dir, artifacts=artifacts)
    module = _load_task_metrics("evaluator-standalone-sdk-surface-discovery")

    scores = _score_task_metric(
        metric=module.SurfaceDiscoveryMetric(),
        task_dir=evaluator_task_dir,
        artifacts=artifacts,
        task_config=task_config,
        attempt=attempt,
    )

    assert scores["task_success"] == [1.0]
    assert scores["verification_score"] == [1.0]
    assert scores["output_schema_valid"] == [1.0]


def test_surface_discovery_metric_rejects_prose_only_answer(evaluator_task_dir: Path, agent_log_dir: Path):
    (agent_log_dir / "final_message.txt").write_text(
        (
            "Use packages/nemo_evaluator_sdk with Evaluator, run_sync, and ExactMatchMetric. "
            "Create the two-row dataset and call Evaluator().run_sync(...) with the expected templates."
        ),
        encoding="utf-8",
    )
    artifacts = AgentArtifacts.from_dir(agent_log_dir)
    task_config = load_agentic_use_task_config(evaluator_task_dir)
    attempt = capture_agent_attempt(task_dir=evaluator_task_dir, artifacts=artifacts)
    module = _load_task_metrics("evaluator-standalone-sdk-surface-discovery")

    scores = _score_task_metric(
        metric=module.SurfaceDiscoveryMetric(),
        task_dir=evaluator_task_dir,
        artifacts=artifacts,
        task_config=task_config,
        attempt=attempt,
    )

    assert scores["task_success"] == [0.0]
    assert scores["output_schema_valid"] == [0.0]


def test_exact_match_metric_requires_runnable_sdk_code(tmp_path: Path, agent_log_dir: Path):
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    (task_dir / "task.toml").write_text(
        """
version = "1.0"

[evaluator.surface]
constraint = "standalone_sdk"
allowed = ["standalone_sdk"]
forbidden = ["cli", "plugin_sdk", "legacy_service"]

[evaluator.expected]
required_terms = ["packages/nemo_evaluator_sdk", "Evaluator", "run_sync", "ExactMatchMetric", "2+2?", "Capital of France?", "0.5"]
""".strip(),
        encoding="utf-8",
    )
    (task_dir / "instruction.md").write_text("Run exact match.", encoding="utf-8")
    (workspace_dir / "solution.py").write_text(
        """
from pathlib import Path
import sys

sys.path.insert(0, str(Path("packages/nemo_evaluator_sdk/src").resolve()))

from nemo_evaluator_sdk import Evaluator, ExactMatchMetric

rows = [
    {"question": "2+2?", "expected": "4", "prediction": "4"},
    {"question": "Capital of France?", "expected": "Paris", "prediction": "Lyon"},
]
result = Evaluator().run_sync(
    metrics=ExactMatchMetric(reference="{{item.expected}}", candidate="{{item.prediction}}"),
    dataset=rows,
)
result.print_summary()
""".strip(),
        encoding="utf-8",
    )
    (agent_log_dir / "final_message.txt").write_text(
        "Wrote workspace/solution.py using packages/nemo_evaluator_sdk; the summary has aggregate score 0.5.",
        encoding="utf-8",
    )
    artifacts = AgentArtifacts.from_dir(agent_log_dir, workspace_dir=workspace_dir)
    task_config = load_agentic_use_task_config(task_dir)
    attempt = capture_agent_attempt(task_dir=task_dir, artifacts=artifacts)
    module = _load_task_metrics("evaluator-standalone-sdk-simple-exact-match")

    scores = _score_task_metric(
        metric=module.ExactMatchEvaluationMetric(),
        task_dir=task_dir,
        artifacts=artifacts,
        task_config=task_config,
        attempt=attempt,
    )

    assert scores["task_success"] == [1.0]
    assert scores["verification_score"] == [1.0]
    assert scores["output_schema_valid"] == [1.0]


def test_exact_match_metric_rejects_code_that_runs_without_expected_scores(tmp_path: Path, agent_log_dir: Path):
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    (task_dir / "task.toml").write_text(
        """
version = "1.0"

[evaluator.surface]
constraint = "standalone_sdk"
allowed = ["standalone_sdk"]
forbidden = ["cli", "plugin_sdk", "legacy_service"]

[evaluator.expected]
required_terms = ["packages/nemo_evaluator_sdk", "Evaluator", "run_sync", "ExactMatchMetric", "2+2?", "Capital of France?", "0.5"]
""".strip(),
        encoding="utf-8",
    )
    (task_dir / "instruction.md").write_text("Run exact match.", encoding="utf-8")
    (workspace_dir / "solution.py").write_text(
        """
from nemo_evaluator_sdk import Evaluator, ExactMatchMetric

# This mentions run_sync but does not perform the required evaluation.
print("not the expected row scores")
print("0.5")
""".strip(),
        encoding="utf-8",
    )
    (agent_log_dir / "final_message.txt").write_text(
        "Wrote workspace/solution.py using packages/nemo_evaluator_sdk for 2+2? and Capital of France?.",
        encoding="utf-8",
    )
    artifacts = AgentArtifacts.from_dir(agent_log_dir, workspace_dir=workspace_dir)
    task_config = load_agentic_use_task_config(task_dir)
    attempt = capture_agent_attempt(task_dir=task_dir, artifacts=artifacts)
    module = _load_task_metrics("evaluator-standalone-sdk-simple-exact-match")

    scores = _score_task_metric(
        metric=module.ExactMatchEvaluationMetric(),
        task_dir=task_dir,
        artifacts=artifacts,
        task_config=task_config,
        attempt=attempt,
    )

    assert scores["task_success"] == [0.0]
    assert scores["output_schema_valid"] == [0.0]


def test_exact_match_metric_rejects_missing_solution_artifact(tmp_path: Path, agent_log_dir: Path):
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    (task_dir / "task.toml").write_text(
        """
version = "1.0"

[evaluator.surface]
constraint = "standalone_sdk"
allowed = ["standalone_sdk"]
forbidden = ["cli", "plugin_sdk", "legacy_service"]

[evaluator.expected]
required_terms = ["packages/nemo_evaluator_sdk", "Evaluator", "run_sync", "ExactMatchMetric", "2+2?", "Capital of France?", "0.5"]
""".strip(),
        encoding="utf-8",
    )
    (task_dir / "instruction.md").write_text("Run exact match.", encoding="utf-8")
    (agent_log_dir / "final_message.txt").write_text(
        "I would use packages/nemo_evaluator_sdk with Evaluator, run_sync, and ExactMatchMetric.",
        encoding="utf-8",
    )
    artifacts = AgentArtifacts.from_dir(agent_log_dir, workspace_dir=workspace_dir)
    task_config = load_agentic_use_task_config(task_dir)
    attempt = capture_agent_attempt(task_dir=task_dir, artifacts=artifacts)
    module = _load_task_metrics("evaluator-standalone-sdk-simple-exact-match")

    scores = _score_task_metric(
        metric=module.ExactMatchEvaluationMetric(),
        task_dir=task_dir,
        artifacts=artifacts,
        task_config=task_config,
        attempt=attempt,
    )

    assert scores["task_success"] == [0.0]
    assert scores["output_schema_valid"] == [0.0]


def _score_task_metric(
    *,
    metric: Metric,
    task_dir: Path,
    artifacts: AgentArtifacts,
    task_config: AgenticUseTaskConfig,
    attempt: CapturedAgentAttempt,
) -> dict[str, list[float]]:
    row = build_evaluator_scoring_row(
        task_dir=task_dir,
        artifacts=artifacts,
        task_config=task_config,
        attempt=attempt,
    )
    scored = score_evaluator_rows([row], additional_metrics=[metric])
    if scored.row_scores and scored.row_scores[0].error:
        raise AssertionError(scored.row_scores[0].error)
    score_values: dict[str, list[float]] = {
        "task_success": [],
        "verification_score": [],
        "output_schema_valid": [],
    }
    for metric_scores in scored.row_scores[0].metrics.values():
        for score in metric_scores:
            if score.name in score_values:
                score_values[score.name].append(score.value)
    return score_values
