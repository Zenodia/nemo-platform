# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Aggregation data structures and computation for metric results."""

import math
from collections import OrderedDict, defaultdict

from nemo_evaluator_sdk.values import (
    AggregatedMetricResult,
    AggregateRangeScore,
    AggregateRubricScore,
    AggregateScore,
    Histogram,
    HistogramBin,
    MetricResult,
    MetricScore,
    Percentiles,
    RubricScoreStat,
    ScoreStats,
)


def add_corpus_scores(aggregated_result: AggregatedMetricResult, corpus_result: MetricResult) -> None:
    """Add corpus-level metric scores to an aggregated result.

    Corpus-level metrics produce single values (not per-row), so they are
    converted to AggregateRangeScore with count=1.

    Args:
        aggregated_result: The aggregated result to add scores to (mutated in place).
        corpus_result: The corpus-level metric result containing scores to add.
    """
    for score in corpus_result.scores:
        value = score.value
        # Create an AggregateRangeScore for the corpus-level metric
        corpus_score = AggregateRangeScore(
            name=score.name,
            count=1,
            nan_count=0,
            sum=value,
            mean=value,
            min=value,
            max=value,
            std_dev=0.0,
            variance=0.0,
            percentiles=Percentiles(
                p10=value,
                p20=value,
                p30=value,
                p40=value,
                p50=value,
                p60=value,
                p70=value,
                p80=value,
                p90=value,
                p100=value,
            ),
            histogram=Histogram(bins=[HistogramBin(lower_bound=value, upper_bound=value, count=1)]),
        )
        aggregated_result.scores.append(corpus_score)


def _compute_percentile(sorted_values: list[float], percentile: float) -> float:
    """Compute a percentile from sorted values using linear interpolation."""
    if not sorted_values:
        return 0.0
    n = len(sorted_values)
    # Use the "exclusive" percentile method (like Excel's PERCENTILE.EXC)
    # Position in the data for the given percentile
    pos = (percentile / 100.0) * (n + 1) - 1
    if pos <= 0:
        return sorted_values[0]
    if pos >= n - 1:
        return sorted_values[-1]
    # Linear interpolation between adjacent values
    lower_idx = int(pos)
    frac = pos - lower_idx
    return sorted_values[lower_idx] + frac * (sorted_values[lower_idx + 1] - sorted_values[lower_idx])


def _compute_percentiles(sorted_values: list[float]) -> Percentiles:
    """Compute standard percentiles from sorted values."""
    return Percentiles(
        p10=_compute_percentile(sorted_values, 10),
        p20=_compute_percentile(sorted_values, 20),
        p30=_compute_percentile(sorted_values, 30),
        p40=_compute_percentile(sorted_values, 40),
        p50=_compute_percentile(sorted_values, 50),
        p60=_compute_percentile(sorted_values, 60),
        p70=_compute_percentile(sorted_values, 70),
        p80=_compute_percentile(sorted_values, 80),
        p90=_compute_percentile(sorted_values, 90),
        p100=_compute_percentile(sorted_values, 100),
    )


def _compute_histogram(values: list[float], num_bins: int = 10) -> Histogram:
    """Compute a histogram from values with the specified number of bins."""
    if not values:
        return Histogram(bins=[])

    min_val = min(values)
    max_val = max(values)

    # Handle edge case where all values are the same
    if min_val == max_val:
        return Histogram(bins=[HistogramBin(lower_bound=min_val, upper_bound=max_val, count=len(values))])

    bin_width = (max_val - min_val) / num_bins
    bins: list[HistogramBin] = []

    for i in range(num_bins):
        lower = min_val + i * bin_width
        upper = min_val + (i + 1) * bin_width
        # Count values in this bin (last bin includes upper bound)
        if i == num_bins - 1:
            count = sum(1 for v in values if lower <= v <= upper)
        else:
            count = sum(1 for v in values if lower <= v < upper)
        bins.append(HistogramBin(lower_bound=lower, upper_bound=upper, count=count))

    return Histogram(bins=bins)


def aggregate_metrics(items: list[MetricResult]) -> AggregatedMetricResult:
    """Aggregate metrics and compute full statistics.

    For range scores: computes percentiles and histogram.
    For rubric scores: computes category distribution and mode.
    """
    # Collect all values per score name for computing distribution stats
    score_values: dict[str, list[float]] = defaultdict(list)

    aggregated_results: dict[str, MetricScore] = {}
    rubric_distribution: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(OrderedDict))
    has_rubric: dict[str, bool] = {}

    # First pass: collect values and compute running stats
    for item in items:
        for score in item.scores:
            if score.name not in aggregated_results:
                # Initialize with all stats fields
                aggregated_results[score.name] = MetricScore(
                    name=score.name,
                    value=0.0,
                    stats=ScoreStats(
                        count=0,
                        sum=0,
                        sum_squared=0,
                        min=None,
                        max=None,
                        mean=0,
                        variance=None,
                        stddev=None,
                        nan_count=0,
                    ),
                )
                # Track if this score has rubric distribution
                has_rubric[score.name] = bool(score.stats and score.stats.rubric_distribution)
                if score.stats and score.stats.rubric_distribution:
                    for rubric_stat in score.stats.rubric_distribution:
                        rubric_distribution[score.name][rubric_stat.label] = {
                            "label": rubric_stat.label,
                            "value": rubric_stat.value,
                            "count": 0,
                        }

            # Increment rubric label per metric score
            if score.stats and score.stats.rubric_distribution:
                for rubric_stat in score.stats.rubric_distribution:
                    if rubric_stat.count:
                        rubric_distribution[score.name][rubric_stat.label]["count"] += 1

            results = aggregated_results[score.name]
            assert results is not None
            assert results.stats is not None

            # Skip NaN values from stats, but track them
            if math.isnan(score.value):
                results.stats.nan_count = (results.stats.nan_count or 0) + 1
                continue

            # Collect value for distribution stats
            score_values[score.name].append(score.value)

            # Update running statistics
            results.stats.count = (results.stats.count or 0) + 1
            results.stats.sum = (results.stats.sum or 0) + score.value
            results.stats.sum_squared = (results.stats.sum_squared or 0) + score.value**2
            results.stats.mean = results.stats.sum / results.stats.count

            # Update min/max
            if results.stats.min is None or score.value < results.stats.min:
                results.stats.min = score.value
            if results.stats.max is None or score.value > results.stats.max:
                results.stats.max = score.value

            # Record mean as the value for backward compatibility
            results.value = results.stats.mean

    # Second pass: compute variance and stddev from collected values
    for score_name, values in score_values.items():
        if not values:
            continue

        results = aggregated_results[score_name]
        assert results.stats is not None

        n = len(values)
        mean = results.stats.mean or 0

        # Population variance: sum((x - mean)^2) / n
        variance = sum((v - mean) ** 2 for v in values) / n if n > 0 else 0
        results.stats.variance = variance
        results.stats.stddev = math.sqrt(variance)

    # Build the full aggregated result with appropriate type
    aggregated_scores: list[AggregateScore] = []
    for score_name, metric_score in aggregated_results.items():
        stats = metric_score.stats
        assert stats is not None

        values = score_values[score_name]

        # Common fields
        base_name = metric_score.name
        base_count = stats.count or 0
        base_nan_count = stats.nan_count or 0
        base_mean = stats.mean
        base_sum = stats.sum if stats.sum is not None else (None if base_mean is None else (base_mean * base_count))
        base_min = stats.min if stats.min is not None else base_mean
        base_max = stats.max if stats.max is not None else base_mean
        base_variance = stats.variance if stats.variance is not None else (None if base_mean is None else 0.0)
        base_std_dev = stats.stddev if stats.stddev is not None else (None if base_mean is None else 0.0)

        if base_count == 0:
            base_sum = None
            base_mean = None
            base_min = None
            base_max = None
            base_variance = None
            base_std_dev = None

        if has_rubric.get(score_name):
            # Rubric score - compute distribution and mode
            rubric_dist = [
                RubricScoreStat(label=r["label"], value=r["value"], count=r["count"])
                for r in rubric_distribution[score_name].values()
            ]
            # Find mode (most frequent category)
            mode_category = None
            if rubric_dist:
                max_count = 0
                for r in rubric_dist:
                    if r.count > max_count:
                        max_count = r.count
                        mode_category = r.label

            aggregated_scores.append(
                AggregateRubricScore(
                    name=base_name,
                    count=base_count,
                    nan_count=base_nan_count,
                    sum=base_sum,
                    mean=base_mean,
                    min=base_min,
                    max=base_max,
                    variance=base_variance,
                    std_dev=base_std_dev,
                    rubric_distribution=rubric_dist,
                    mode_category=mode_category,
                )
            )
        else:
            # Range score - compute percentiles and histogram
            if values:
                sorted_values = sorted(values)
                percentiles = _compute_percentiles(sorted_values)
                histogram = _compute_histogram(values)
            else:
                # Empty results - percentile distribution is undefined when no valid samples were scored.
                percentiles = None
                histogram = Histogram(bins=[])

            aggregated_scores.append(
                AggregateRangeScore(
                    name=base_name,
                    count=base_count,
                    nan_count=base_nan_count,
                    sum=base_sum,
                    mean=base_mean,
                    min=base_min,
                    max=base_max,
                    variance=base_variance,
                    std_dev=base_std_dev,
                    percentiles=percentiles,
                    histogram=histogram,
                )
            )

    return AggregatedMetricResult(scores=aggregated_scores)
