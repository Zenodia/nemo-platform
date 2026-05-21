# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the improvement/strategies/ submodule."""

from __future__ import annotations

from pathlib import Path

from nemo_agents_plugin.improvement.models import GapCategory, Hypothesis
from nemo_agents_plugin.improvement.strategies.base import ImprovementStrategy
from nemo_agents_plugin.improvement.strategies.skills import SkillsOptimizerStrategy


def test_skills_optimizer_implements_strategy_protocol() -> None:
    strat = SkillsOptimizerStrategy()
    assert isinstance(strat, ImprovementStrategy)
    assert strat.name == "skills"


def test_skills_optimizer_writable_paths_uses_skills_path(tmp_path: Path) -> None:
    strat = SkillsOptimizerStrategy(skills_path=".my/skills")
    paths = strat.writable_paths(tmp_path)
    assert paths == [tmp_path / ".my/skills"]


def test_skills_optimizer_writable_paths_default(tmp_path: Path) -> None:
    strat = SkillsOptimizerStrategy()
    paths = strat.writable_paths(tmp_path)
    assert paths == [tmp_path / ".agents/skills"]


def test_skills_optimizer_render_prompt_includes_constraints(tmp_path: Path) -> None:
    strat = SkillsOptimizerStrategy(skills_path=".skills")
    h = Hypothesis(
        cluster_id="c1",
        eval_names=["eval-a"],
        root_cause="missing skill",
        category=GapCategory.MISSING_SKILL,
        proposed_fix="add a new skill",
        affected_files=[".skills/new.md"],
        expected_impact="should pass",
        confidence=0.7,
    )
    prompt = strat.render_prompt(h, tmp_path)
    assert ".skills" in prompt
    assert "eval-a" in prompt
    assert "missing skill" in prompt
