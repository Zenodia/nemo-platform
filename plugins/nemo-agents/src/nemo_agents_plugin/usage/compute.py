# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Compute-units cost proxy from a user-supplied total-params value.

The optimization-canonical metric for agent runs::

    compute_units = total_tokens * total_params_b

A transparent ranking signal that rewards using fewer tokens AND moving
work to a smaller model.  It is *not* a dollar estimate — vendor pricing
is intentionally out of scope for this metric.

``total_params_b`` is the model's full parameter count (in billions),
not the per-token active count.  Using totals lets the metric stand in
for memory/capacity cost — a 32B-total / 8B-active MoE scores at 32B
because that's roughly its VRAM footprint.  Per-token compute is a
separate concern and is not modelled here.

``total_params_b`` is supplied by the caller; when absent, the metric
returns ``None`` rather than guessing.
"""

from __future__ import annotations

import math


def compute_units_for(total_params_b: float | None, total_tokens: int | None) -> int | None:
    """Return ``total_tokens × total_params_b``, rounded, or ``None``.

    Returns ``None`` when either input is absent — the caller (CLI) is
    responsible for deciding whether that's a "no usage on disk" signal
    or a "user didn't pass --total-params" signal.

    Rejects non-finite or non-positive ``total_params_b`` with
    :class:`ValueError`: zero would silently flatten every task's
    compute_units to 0 (a "real-looking" total that ranks below any
    positive baseline), negative values produce nonsense deltas, and
    NaN/inf would propagate into ``int(round(...))`` as uncaught
    ``ValueError``/``OverflowError``.
    """
    if total_params_b is None or total_tokens is None:
        return None
    if not math.isfinite(total_params_b) or total_params_b <= 0:
        raise ValueError(f"total_params_b must be a finite positive number, got {total_params_b}")
    return int(round(total_tokens * total_params_b))
