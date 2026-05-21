# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""JSON renderer for usage reports.

Matches the ``nemo agents`` plugin's existing convention of emitting
indented JSON via :func:`json.dumps` with ``indent=2``.
"""

from __future__ import annotations

import json

from nemo_agents_plugin.usage.models import BatchUsageReport, UsageReport


def render_json(report: UsageReport | BatchUsageReport) -> str:
    """Serialize *report* to a stable indented-JSON string."""
    return json.dumps(report.model_dump(mode="json"), indent=2)
