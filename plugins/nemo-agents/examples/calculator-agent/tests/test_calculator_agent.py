# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for the calculator-agent config, packaging, and entry points."""

import json
from importlib.metadata import entry_points
from importlib.resources import files

import yaml
from calculator_agent.register import CalculatorToolConfig


class TestCalculatorConfig:
    def test_config_registers_calculator_type(self):
        assert CalculatorToolConfig._typed_model_name == "calculator"

    def test_default_include_list(self):
        config = CalculatorToolConfig()
        assert set(config.include) == {"add", "subtract", "multiply", "divide", "compare"}


class TestPackageData:
    def test_agent_yml_bundled_and_valid(self):
        content = files("calculator_agent").joinpath("calculator-agent.yml").read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        assert "llms" in config
        assert "workflow" in config
        assert config["workflow"]["_type"] == "react_agent"

    def test_eval_data_bundled_and_valid(self):
        content = files("calculator_agent").joinpath("calculator-eval-data.json").read_text(encoding="utf-8")
        data = json.loads(content)
        assert isinstance(data, list)
        assert data
        assert all("question" in item and "answer" in item for item in data)

    def test_eval_yml_bundled_and_valid(self):
        content = files("calculator_agent").joinpath("calculator-eval.yml").read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        assert "eval" in config
        assert "llms" in config

    def test_optimize_yml_bundled_and_valid(self):
        content = files("calculator_agent").joinpath("calculator-optimize.yml").read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        assert "optimizer" in config
        assert "eval" in config


class TestEntryPoints:
    def test_nat_components_entry_point_registered(self):
        eps = entry_points(group="nat.components")
        names = {ep.name for ep in eps}
        assert "nemo_agents_example_calculator" in names

    def test_entry_point_resolves_to_register_module(self):
        eps = entry_points(group="nat.components")
        ep = next(ep for ep in eps if ep.name == "nemo_agents_example_calculator")
        assert ep.value == "calculator_agent.register"
