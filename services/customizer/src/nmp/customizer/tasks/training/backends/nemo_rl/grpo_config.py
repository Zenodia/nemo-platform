# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

"""TrainingStepConfig → NeMo RL YAML configuration generation.

This module handles configuration generation for GRPO training type,
converting the internal TrainingStepConfig format to NeMo RL's YAML format.

Example of similar config but for DPO training type
- services/customizer/src/nmp/customizer/tasks/training/backends/nemo_rl/dpo_config.py
"""

import logging
from typing import Any

from nmp.customizer.app.jobs.context import NMPJobContext
from nmp.customizer.tasks.training.schemas import (
    TrainingStepConfig,
)

logger = logging.getLogger(__name__)


def compile_grpo_config(
    training_config: TrainingStepConfig,
    job_ctx: NMPJobContext,
) -> dict[str, Any]:
    """Compile TrainingStepConfig to GRPO configuration.

    Args:
        training_config: The training step configuration
        job_ctx: Job context

    Returns:
        Configuration dict for NeMo RL GRPO training
    """
    # TODO: Implement GRPO config compilation
    print(training_config)
    print(job_ctx)
    raise NotImplementedError("GRPO config compilation not yet implemented")
