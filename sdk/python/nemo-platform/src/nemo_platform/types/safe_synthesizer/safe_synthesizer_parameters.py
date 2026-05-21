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

from typing import Optional

from ..._models import BaseModel
from .data_parameters import DataParameters
from .generate_parameters import GenerateParameters
from .pii_replacer_config import PIIReplacerConfig
from .training_hyperparams import TrainingHyperparams
from .evaluation_parameters import EvaluationParameters
from .time_series_parameters import TimeSeriesParameters
from .differential_privacy_hyperparams import DifferentialPrivacyHyperparams

__all__ = ["SafeSynthesizerParameters"]


class SafeSynthesizerParameters(BaseModel):
    """Main configuration class for the Safe Synthesizer pipeline.

    This is the top-level configuration class that orchestrates all aspects of
    synthetic data generation including training, generation, privacy, evaluation,
    and data handling. It provides validation to ensure parameter compatibility.
    """

    data: Optional[DataParameters] = None
    """
    Configuration for grouping, ordering, and splitting input data for training and
    evaluation.
    """

    evaluation: Optional[EvaluationParameters] = None
    """Configuration for evaluating synthetic data quality and privacy.

    This class controls which evaluation metrics are computed and how they are
    configured. It includes privacy attack evaluations, statistical quality metrics,
    and downstream machine learning performance assessments.
    """

    generation: Optional[GenerateParameters] = None
    """Configuration parameters for synthetic data generation.

    These parameters control how synthetic data is generated after the model is
    trained. They affect the quality, diversity, and validity of the generated
    synthetic records.
    """

    privacy: Optional[DifferentialPrivacyHyperparams] = None
    """Hyperparameters for differential privacy during training.

    These parameters configure differential privacy (DP) training using DP-SGD
    algorithm. When enabled, they provide formal privacy guarantees by adding
    calibrated noise during training.
    """

    replace_pii: Optional[PIIReplacerConfig] = None
    """Configuration for PII replacer.

    Defines how PII data should be detected and replaced in a dataset.
    """

    time_series: Optional[TimeSeriesParameters] = None
    """Configuration for time-series mode in the Safe Synthesizer pipeline.

    Controls whether a dataset is treated as time-series data, including timestamp
    column selection, interval inference, and format validation. The time-series
    pipeline is currently experimental.
    """

    training: Optional[TrainingHyperparams] = None
    """Hyperparameters that control the training process behavior.

    This class contains all the fine-tuning hyperparameters that control how the
    model learns, including learning rates, batch sizes, LoRA configuration, and
    optimization settings. These parameters directly affect training performance and
    quality.
    """
