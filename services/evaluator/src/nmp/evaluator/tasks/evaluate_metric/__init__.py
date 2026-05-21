# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
"""Evaluate a metric with NeMo Evaluator.

This module provides the containerized task for running custom evaluations.
"""

from nmp.evaluator.tasks.evaluate_metric.__main__ import (
    evaluate_metric,
    metric_evaluation_entrypoint,
    metric_evaluation_entrypoint_args,
    run,
)

__all__ = [
    "metric_evaluation_entrypoint",
    "metric_evaluation_entrypoint_args",
    "evaluate_metric",
    "run",
]
