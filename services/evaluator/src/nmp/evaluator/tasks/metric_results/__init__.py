# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Metric results task package.

This task uploads evaluation results to the Jobs and Files APIs.
"""

from nmp.evaluator.tasks.metric_results.__main__ import run

__all__ = ["run"]
