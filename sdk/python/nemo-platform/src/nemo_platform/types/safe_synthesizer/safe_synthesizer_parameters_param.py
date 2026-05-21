# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .data_parameters_param import DataParametersParam
from .generate_parameters_param import GenerateParametersParam
from .pii_replacer_config_param import PIIReplacerConfigParam
from .training_hyperparams_param import TrainingHyperparamsParam
from .evaluation_parameters_param import EvaluationParametersParam
from .time_series_parameters_param import TimeSeriesParametersParam
from .differential_privacy_hyperparams_param import DifferentialPrivacyHyperparamsParam

__all__ = ["SafeSynthesizerParametersParam"]


class SafeSynthesizerParametersParam(TypedDict, total=False):
    """Main configuration class for the Safe Synthesizer pipeline.

    This is the top-level configuration class that orchestrates all aspects of
    synthetic data generation including training, generation, privacy, evaluation,
    and data handling. It provides validation to ensure parameter compatibility.
    """

    data: DataParametersParam
    """
    Configuration for grouping, ordering, and splitting input data for training and
    evaluation.
    """

    evaluation: EvaluationParametersParam
    """Configuration for evaluating synthetic data quality and privacy.

    This class controls which evaluation metrics are computed and how they are
    configured. It includes privacy attack evaluations, statistical quality metrics,
    and downstream machine learning performance assessments.
    """

    generation: GenerateParametersParam
    """Configuration parameters for synthetic data generation.

    These parameters control how synthetic data is generated after the model is
    trained. They affect the quality, diversity, and validity of the generated
    synthetic records.
    """

    privacy: DifferentialPrivacyHyperparamsParam
    """Hyperparameters for differential privacy during training.

    These parameters configure differential privacy (DP) training using DP-SGD
    algorithm. When enabled, they provide formal privacy guarantees by adding
    calibrated noise during training.
    """

    replace_pii: PIIReplacerConfigParam
    """Configuration for PII replacer.

    Defines how PII data should be detected and replaced in a dataset.
    """

    time_series: TimeSeriesParametersParam
    """Configuration for time-series mode in the Safe Synthesizer pipeline.

    Controls whether a dataset is treated as time-series data, including timestamp
    column selection, interval inference, and format validation. The time-series
    pipeline is currently experimental.
    """

    training: TrainingHyperparamsParam
    """Hyperparameters that control the training process behavior.

    This class contains all the fine-tuning hyperparameters that control how the
    model learns, including learning rates, batch sizes, LoRA configuration, and
    optimization settings. These parameters directly affect training performance and
    quality.
    """
