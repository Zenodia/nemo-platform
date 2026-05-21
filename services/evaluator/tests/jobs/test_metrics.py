# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from nemo_evaluator_sdk import ExactMatchMetric
from nemo_evaluator_sdk.values import DatasetRows, Model, SecretRef
from nmp.evaluator.app.jobs.metrics import EnvironmentVariable, _get_model_env_secret
from nmp.evaluator.app.values import (
    MetricJob,
    MetricOfflineJob,
    MetricOnlineJob,
)
from pytest_mock import MockerFixture

test_metric = ExactMatchMetric(reference="reference", candidate="candidate")
test_dataset = DatasetRows(rows=[{"reference": "a", "candidate": "b"}])


@pytest.mark.parametrize(
    "desc,job",
    [
        (
            "no model to evaluate with offline job",
            MetricOfflineJob(
                metric=test_metric,
                dataset=test_dataset,
            ),
        ),
        (
            "no api key set",
            MetricOnlineJob(
                metric=test_metric,
                dataset=test_dataset,
                model=Model(name="workspace/my-model", url="http://nim.test"),
                prompt_template="hello world",
            ),
        ),
    ],
)
def test_get_model_env_secret_no_secret(desc: str, job: MetricJob):
    secret = _get_model_env_secret(job)
    assert secret is None, f"expected no model secret when {desc}"


def test_get_model_env_secret():
    job = MetricOnlineJob(
        metric=test_metric,
        dataset=test_dataset,
        model=Model(
            name="workspace/my-model",
            url="http://nim.test",
            api_key_secret=SecretRef(root="my-secret"),
        ),
        prompt_template="hello world",
    )
    secret = _get_model_env_secret(job)
    # Env var name uses underscores (launcher converts hyphens to underscores)
    assert secret == EnvironmentVariable({"name": "my_secret", "from_secret": {"name": "my-secret"}})


def test_get_model_env_secret_raises_when_secret_has_no_env(mocker: MockerFixture):
    mocker.patch.object(Model, "api_key_env", new=property(lambda self: None))
    job = MetricOnlineJob(
        metric=test_metric,
        dataset=test_dataset,
        model=Model(
            name="workspace/my-model",
            url="http://nim.test",
            api_key_secret=SecretRef(root="my-secret"),
        ),
        prompt_template="hello world",
    )

    with pytest.raises(ValueError, match=r"model\.api_key_env must be set when model\.api_key_secret is configured"):
        _get_model_env_secret(job)
