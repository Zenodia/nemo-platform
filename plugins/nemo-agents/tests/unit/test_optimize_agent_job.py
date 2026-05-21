# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for ``OptimizeAgentJob`` local runner behavior."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import yaml
from nemo_agents_plugin.jobs.optimize_agent import OptimizeAgentJob
from nemo_platform_plugin.job_context import JobContext


def test_run_repoints_outputs_to_persistent_results(tmp_path: Path, ctx: JobContext) -> None:
    optimize_yaml = tmp_path / "optimize.yml"
    optimize_yaml.write_text(
        """
llms:
  llm:
    _type: openai
    model_name: test-model
eval:
  general:
    output_dir: eval/calculator
optimizer:
  output_path: optimizer_results/calculator
""".strip()
    )

    captured: dict[str, Any] = {}

    def _fake_run(cmd: list[str], *, check: bool, cwd: Path) -> subprocess.CompletedProcess[str]:
        captured["cmd"] = cmd
        captured["check"] = check
        captured["cwd"] = cwd
        captured["injected_config"] = yaml.safe_load((cwd / cmd[3]).read_text(encoding="utf-8"))
        return subprocess.CompletedProcess(cmd, 0)

    with patch("nemo_agents_plugin.jobs.optimize_agent.subprocess.run", side_effect=_fake_run):
        result = OptimizeAgentJob().run({"optimize_config": str(optimize_yaml), "workspace": "default"}, ctx=ctx)

    assert result == {"status": "completed", "returncode": 0}
    assert captured["check"] is True
    assert captured["cwd"] == optimize_yaml.parent
    cmd = captured["cmd"]
    assert isinstance(cmd, list)
    assert cmd[:3] == ["nat", "optimize", "--config_file"]
    assert str(cmd[3]).startswith(".injected-optimize-")
    assert cmd[4:] == []

    injected_config = cast(dict[str, Any], captured["injected_config"])
    assert injected_config["eval"]["general"]["output_dir"] == str(
        ctx.storage.persistent / "results" / "eval" / "calculator"
    )
    assert injected_config["optimizer"]["output_path"] == str(
        ctx.storage.persistent / "results" / "optimizer_results" / "calculator"
    )
