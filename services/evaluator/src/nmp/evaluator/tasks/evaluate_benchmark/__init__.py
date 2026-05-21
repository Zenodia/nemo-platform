# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
"""Evaluate a benchmark with NeMo Evaluator.

This module provides the containerized task for running benchmark evaluations,
which evaluate all metrics in a benchmark against a dataset.
"""

from nmp.evaluator.tasks.evaluate_benchmark.__main__ import (
    benchmark_evaluation_entrypoint,
    benchmark_evaluation_entrypoint_args,
    evaluate_benchmark,
    run,
)

__all__ = [
    "benchmark_evaluation_entrypoint",
    "benchmark_evaluation_entrypoint_args",
    "evaluate_benchmark",
    "run",
]
