# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Exact-match metric runtime implementation."""

from nemo_platform.beta.evaluator.metrics.base import normalize_text
from nemo_platform.beta.evaluator.metrics.template_rendering import render_reference_and_candidate, template_metric_repr
from nemo_platform.beta.evaluator.values.metrics import ExactMatch
from nemo_platform.beta.evaluator.values.results import MetricResult, MetricScore

__all__ = ["ExactMatchMetric"]


class ExactMatchMetric(ExactMatch):
    """Exact-match metric runtime for evaluator-driven execution.

    Evaluator-driven runs expose dataset values through ``item`` and generated
    model outputs through ``sample.output_text`` for online execution.
    """

    def score_names(self) -> list[str]:
        """Return score keys emitted by this metric.

        Returns:
            Single-item list containing the exact-match metric type name.
        """
        return [self.type.value]

    async def compute_scores(self, item: dict, sample: dict) -> MetricResult:
        """Compute structured metric output for one item/sample pair.

        The algorithm renders reference and candidate text from templates, then
        normalizes both strings (case, punctuation, articles, and whitespace)
        before equality comparison.

        Args:
            item: Original dataset row.
            sample: Generated-sample payload used for candidate extraction.

        Returns:
            ``MetricResult`` with one exact-match score entry.

        Raises:
            TypeError: If rendered reference or candidate is not a string.
            ValueError: If template rendering fails or ``candidate`` is omitted
                and ``sample.output_text`` is missing.
        """
        ground_truth, prediction = render_reference_and_candidate(
            metric_repr=template_metric_repr(self),
            metric_name=self.__class__.__name__,
            reference_template=self.reference,
            candidate_template=self.candidate,
            item=item,
            sample=sample,
        )
        score = int(normalize_text(prediction) == normalize_text(ground_truth))
        return MetricResult(scores=[MetricScore(name=self.type.value, value=score)])
