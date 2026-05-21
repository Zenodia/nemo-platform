# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import mock

import pytest
from nmp.evaluator.config import EvaluatorSettings


def test_defaults():
    settings = EvaluatorSettings()
    assert settings.recreate_existing_system_entities is False
    assert settings.jobs.configs_dir == "/configs"
    assert settings.evalfactory.agentic_eval == "nvcr.io/nvidia/eval-factory/agentic_eval:26.01"


@pytest.mark.unit_test
@mock.patch.dict(
    os.environ,
    {
        "NMP_EVALUATOR_RECREATE_EXISTING_SYSTEM_ENTITIES": "true",
        "NMP_EVALUATOR_JOBS_CONFIGS_DIR": "/new/configs/path",
        "NMP_EVALUATOR_EVALFACTORY_AGENTIC_EVAL": "my-container",
    },
)
def test_env_override():
    settings = EvaluatorSettings()
    assert settings.recreate_existing_system_entities is True
    assert settings.jobs.configs_dir == "/new/configs/path"
    assert settings.evalfactory.agentic_eval == "my-container"
