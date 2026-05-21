# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Optional metric capabilities and shared helpers for evaluator SDK runtime."""

# Migrated from: services/evaluator/src/nmp/evaluator/app/metrics/base.py

import re
import string
from typing import Awaitable, Callable, Protocol, runtime_checkable

from nemo_evaluator_sdk.values import SecretRef
from nemo_evaluator_sdk.values.results import MetricResult

SecretResolver = Callable[[str], Awaitable[str | None]]


@runtime_checkable
class Metric(Protocol):
    """Structural contract for SDK runtime metrics used by generic evaluator code.

    This protocol describes what execution and orchestration code may rely on
    when working with a metric instance. In particular, ``type`` is treated as
    a string identifier. Built-in metrics may expose existing ``MetricType``
    values for schema compatibility, but custom metrics should use plain
    strings:

    - a built-in ``MetricType`` member
    - a plain string such as ``"my-custom-metric"``

    Generic consumers must therefore treat ``type`` as a string identifier and
    must not depend on enum-only APIs such as ``.value``. Callers that need to
    normalize supported runtime shapes should use ``metric_type_name(...)``.
    """

    @property
    def type(self) -> str:
        """Return the public metric key/type identifier.

        Examples:
            Built-in runtime metrics may expose ``MetricType.BLEU``.

            Custom metrics may expose a plain string such as
            ``"my-custom-metric"``.
        """
        ...

    async def compute_scores(self, item: dict, sample: dict) -> MetricResult:
        """Compute structured score output for one item/sample pair."""
        ...

    def score_names(self) -> list[str]:
        """Return canonical score names emitted by this metric."""
        ...


@runtime_checkable
class CorpusMetric(Protocol):
    """Protocol for metrics that also emit corpus-level scores."""

    async def compute_corpus_scores(self, items: list[dict], samples: list[dict]) -> MetricResult | None:
        """Compute corpus-level scores across all evaluated rows.

        Args:
            items: Original dataset rows.
            samples: Sample payloads paired to ``items``.

        Returns:
            Optional corpus-level metric result.
        """
        ...


@runtime_checkable
class MetricWithSecrets(Protocol):
    """Protocol for metrics that require secrets (e.g., API keys)."""

    def secrets(self) -> dict[str, SecretRef]:
        """
        Returns a dictionary of environment variables to the secret reference.
        Used by the job flow to set up environment variables.
        """
        ...

    async def resolve_secrets(self, secret_resolver: SecretResolver) -> None:
        """
        Resolve secrets using the provided resolver function.
        Called before the metric is used for evaluation.
        """
        ...


@runtime_checkable
class MetricWithPreflight(Protocol):
    """Protocol for metrics that need one-time setup before parallel evaluation starts."""

    async def preflight(self) -> None:
        """Run one-time preflight (e.g., capability detection) before processing rows."""
        ...


# TODO: migrate the rest of the protocols from services/evaluator/src/nmp/evaluator/app/metrics/base.py


def normalize_text(s: str) -> str:
    """Normalize free-form text for token/equality-based metric comparisons."""
    if not s:
        return ""
    # lower case
    s = s.lower()
    # remove punctuation
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    # remove articles
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    # collapse whitespace
    s = " ".join(s.split())
    return s
