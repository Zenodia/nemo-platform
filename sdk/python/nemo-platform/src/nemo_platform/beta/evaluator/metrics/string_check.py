# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""String-check metric runtime implementation."""

from nemo_platform.beta.evaluator.metrics.template_rendering import (
    build_template_context,
    render_template_or_raise,
    template_metric_repr,
)
from nemo_platform.beta.evaluator.values.metrics import StringCheck, StringCheckOperation
from nemo_platform.beta.evaluator.values.results import MetricResult, MetricScore

__all__ = ["StringCheckMetric", "StringCheckOperation"]


class StringCheckMetric(StringCheck):
    """String-comparison metric with operator-based checks."""

    def score_names(self) -> list[str]:
        """Return score keys emitted by this metric."""
        return [self.type.value]

    async def compute_scores(self, item: dict, sample: dict) -> MetricResult:
        """Compute the scores for the metric."""
        context = build_template_context(item, sample)
        metric_repr = template_metric_repr(self)
        left_value = render_template_or_raise(
            template_name="left_template",
            template=self.left_template,
            context=context,
            item=item,
            sample=sample,
            metric_repr=metric_repr,
        )
        right_value = render_template_or_raise(
            template_name="right_template",
            template=self.right_template,
            context=context,
            item=item,
            sample=sample,
            metric_repr=metric_repr,
        )

        if not isinstance(left_value, str):
            raise TypeError("The left value must be a string.")
        if not isinstance(right_value, str):
            raise TypeError("The right value must be a string.")

        # Perform the requested string comparison on the rendered operands.
        if self.operation in ["equals", "=="]:
            score = left_value == right_value
        elif self.operation in ["!=", "<>", "not equals"]:
            score = left_value != right_value
        elif self.operation in ["contains"]:
            score = right_value in left_value
        elif self.operation in ["not contains"]:
            score = right_value not in left_value
        elif self.operation in ["startswith"]:
            score = left_value.startswith(right_value)
        elif self.operation in ["endswith"]:
            score = left_value.endswith(right_value)
        else:
            raise ValueError(f"Unsupported operation: {self.operation}")

        return MetricResult(scores=[MetricScore(name=self.type.value, value=1.0 if score else 0.0)])
