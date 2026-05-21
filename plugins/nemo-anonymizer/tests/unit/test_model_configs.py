# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for ``app/model_configs.py``."""

from __future__ import annotations

import data_designer.config as dd
import pytest
import yaml
from nemo_anonymizer_plugin.app.errors import AnonymizerInvalidConfigError
from nemo_anonymizer_plugin.app.model_configs import (
    SelectedModelsOverrides,
    build_model_configs_yaml,
    validate_selected_models_have_model_configs,
)


def _mc(alias: str, *, provider: str = "ws/p", model: str = "test/model") -> dd.ModelConfig:
    return dd.ModelConfig(alias=alias, model=model, provider=provider)


def test_emits_only_model_configs_when_no_selections() -> None:
    yaml_body = build_model_configs_yaml(model_configs=[_mc("a"), _mc("b")])
    parsed = yaml.safe_load(yaml_body)
    assert "model_configs" in parsed
    assert {mc["alias"] for mc in parsed["model_configs"]} == {"a", "b"}
    assert "selected_models" not in parsed


def test_emits_selected_models_when_provided() -> None:
    overrides = SelectedModelsOverrides(
        detection={"entity_detector": "a", "entity_validator": ["a", "b"]},
        replace={"replacement_generator": "a"},
    )
    yaml_body = build_model_configs_yaml(model_configs=[_mc("a"), _mc("b")], selected_models=overrides)
    parsed = yaml.safe_load(yaml_body)
    assert parsed["selected_models"]["detection"]["entity_validator"] == ["a", "b"]
    assert parsed["selected_models"]["replace"] == {"replacement_generator": "a"}
    assert "rewrite" not in parsed["selected_models"]


def test_skips_empty_overrides() -> None:
    overrides = SelectedModelsOverrides()
    yaml_body = build_model_configs_yaml(model_configs=[_mc("a")], selected_models=overrides)
    parsed = yaml.safe_load(yaml_body)
    assert "selected_models" not in parsed


def test_rejects_selected_models_without_model_configs() -> None:
    overrides = SelectedModelsOverrides(detection={"entity_detector": "a"})

    with pytest.raises(AnonymizerInvalidConfigError, match="selected_models requires model_configs"):
        validate_selected_models_have_model_configs(model_configs=None, selected_models=overrides)


def test_allows_empty_selected_models_without_model_configs() -> None:
    validate_selected_models_have_model_configs(model_configs=None, selected_models=SelectedModelsOverrides())


def test_rejects_list_for_scalar_detection_role_at_api_boundary() -> None:
    """List for a scalar role survives our loose dict typing but upstream rejects it.

    ``SelectedModelsOverrides.detection`` is typed as
    ``dict[str, str | list[str]]`` because some roles legitimately accept a
    pool (``entity_validator``). Roles like ``entity_detector`` are scalar
    only — upstream's ``DetectionModelSelection.entity_detector: str`` rejects
    a list. We catch that at the plugin boundary by round-tripping through
    upstream's ``parse_model_configs``.
    """
    overrides = SelectedModelsOverrides(
        detection={"entity_detector": ["a", "b"]},
    )
    with pytest.raises(AnonymizerInvalidConfigError):
        build_model_configs_yaml(model_configs=[_mc("a")], selected_models=overrides)
