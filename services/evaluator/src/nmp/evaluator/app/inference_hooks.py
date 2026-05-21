# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging

import nemo_evaluator_sdk.inference as sdk_inference
from nemo_evaluator_sdk.enums import ModelFormat
from nemo_evaluator_sdk.inference import PostprocessResponse, PreprocessRequest
from nemo_evaluator_sdk.metrics.llm_judge import LLMJudgeMetric
from nemo_evaluator_sdk.values.params import RunConfig, RunConfigOnlineModel
from nmp.evaluator.app.jobs.progress_tracking import ProgressTracking


class ProgressTrackingHook(PostprocessResponse):
    """
    Increment the samples_processed count for progress tracking
    """

    def __init__(self, progress_tracking: ProgressTracking):
        self.progress_tracking = progress_tracking

    def postprocess(self, response, id=None) -> dict:
        self.progress_tracking.increment_samples_processed()
        return response


def new_hooks(
    params: RunConfig | LLMJudgeMetric | None,
    model_format: ModelFormat | None = ModelFormat.NVIDIA_NIM,
    logger: logging.Logger | None = None,
) -> tuple[list[PreprocessRequest], list[PostprocessResponse]]:
    """Initialize preprocess and postprocess hooks for the inference."""
    if isinstance(params, (RunConfigOnlineModel, LLMJudgeMetric)):
        return sdk_inference.new_hooks(params, model_format=model_format, logger=logger)
    return sdk_inference.new_hooks(None, model_format=model_format, logger=logger)
