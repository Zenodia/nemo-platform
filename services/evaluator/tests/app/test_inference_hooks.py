# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from nemo_evaluator_sdk.enums import ModelFormat
from nemo_evaluator_sdk.inference import LogHook
from nemo_evaluator_sdk.values import RunConfig, RunConfigOnlineModel
from nmp.evaluator.app import inference_hooks
from pytest_mock import MockerFixture


def test_new_hooks_no_params():
    pre, post = inference_hooks.new_hooks(None)
    assert len(pre) == 1, "at least log hook is initialized"
    assert isinstance(pre[0], LogHook), "at least log hook is initialized"
    assert len(post) == 1, "at least log hook is initialized"
    assert isinstance(post[0], LogHook), "log hook"
    assert pre[0] is post[0], "pre and post should have the same instance of log hook"


def test_new_hooks_offline_params():
    params = RunConfig()
    pre, post = inference_hooks.new_hooks(params)

    assert len(pre) == 1, "at least log hook is initialized"
    assert isinstance(pre[0], LogHook), "at least log hook is initialized"
    assert len(post) == 1, "at least log hook is initialized"
    assert isinstance(post[0], LogHook), "log hook"
    assert pre[0] is post[0], "pre and post should have the same instance of log hook"


def test_new_hooks_delegates_to_sdk(mocker: MockerFixture):
    expected = (["pre"], ["post"])
    new_hooks = mocker.patch("nmp.evaluator.app.inference_hooks.sdk_inference.new_hooks", return_value=expected)
    params = RunConfigOnlineModel()
    logger = mocker.Mock()

    result = inference_hooks.new_hooks(params, model_format=ModelFormat.OPEN_AI, logger=logger)

    assert result is expected
    new_hooks.assert_called_once_with(params, model_format=ModelFormat.OPEN_AI, logger=logger)


def test_progress_tracking_hook_increments_and_returns_response(mocker: MockerFixture):
    progress = mocker.Mock()
    hook = inference_hooks.ProgressTrackingHook(progress)
    response = {"choices": [{"message": {"content": "ok"}}]}

    assert hook.postprocess(response) is response
    progress.increment_samples_processed.assert_called_once_with()
