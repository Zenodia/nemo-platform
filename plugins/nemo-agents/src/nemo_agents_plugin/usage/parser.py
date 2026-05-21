# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Parse ``nat_runner.py``'s on-disk artifacts into typed reports.

The parser is pure: it reads ``result.json`` files and produces a
:class:`~nemo_agents_plugin.usage.models.UsageReport` or
:class:`~nemo_agents_plugin.usage.models.BatchUsageReport`.  It does not
score ``compute_units``; that is layered on by the CLI after parsing so
the parser stays trivially testable.

Sniff order (in :func:`parse_path`):

1. ``path`` is a file → treated as a single result.json (any name) and
   loaded into a :class:`UsageReport`.  Required keys are checked so that
   pointing at an unrelated JSON document (a config, a JSONL log, etc.)
   produces a clean :class:`UsageParseError` rather than a default-filled
   garbage report.
2. ``path`` is a directory directly containing ``result.json`` (one
   ``<ts>-<task>/`` run) → single :class:`UsageReport`.  When such a
   directory *also* has run-shaped subdirectories, the top-level
   ``result.json`` wins and a warning is logged so the user can
   disambiguate.
3. ``path`` is a directory whose immediate children are run dirs each
   holding ``result.json`` (a ``nat-jobs/`` tree, also the layout
   produced by staging a fileset download into a tempdir) →
   :class:`BatchUsageReport`.  Children without ``result.json`` are
   skipped with a warning.  A child whose ``result.json`` exists but
   fails to load (truncated JSON, schema mismatch) is also skipped with
   a warning and counted in ``unparseable_runs`` so the surrounding
   runs still produce a useful report.
4. Otherwise → :class:`UsageParseError`.

``metrics.{prompt,completion,total}_tokens`` pass through verbatim.  ``None``
is preserved — it is a valid signal that the agent backend did not emit
parseable usage.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from nemo_agents_plugin.usage.models import BatchUsageReport, TaskUsage, UsageReport
from pydantic import ValidationError

logger = logging.getLogger(__name__)

# A parsed JSON document must contain BOTH of these keys to be accepted
# as result.json-shaped.  Singletons like {"task": ...} are common in
# unrelated JSON (k8s manifests, CI configs); requiring both anchors
# recognition tightly enough to reject them while still accepting every
# real result.json (both keys are written unconditionally upstream).
_REQUIRED_KEYS = frozenset({"task", "metrics"})


class UsageParseError(ValueError):
    """Raised when *path* does not point to a recognizable nat_runner output."""


def parse_path(path: Path) -> UsageReport | BatchUsageReport:
    """Sniff *path* and return the appropriate report.

    *path* may be:
    - a ``result.json`` file,
    - a single ``<ts>-<task>/`` run directory containing ``result.json``,
    - a ``nat-jobs/`` directory containing many run subdirectories.
    """
    if path.is_file():
        # Any file at this position is treated as a result.json regardless of
        # name — fixtures, backups, and renamed copies all parse.
        task = _load_task(path)
        return UsageReport(task=task)

    if not path.is_dir():
        raise UsageParseError(f"not a file or directory: {path}")

    direct_result = path / "result.json"
    if direct_result.is_file():
        # Disambiguation: warn if run-shaped subdirectories also exist; the
        # user almost certainly has a snapshot they intended to inspect, but
        # the silent precedence (top-level wins) is a known footgun.
        sibling_runs = [c for c in path.iterdir() if c.is_dir() and (c / "result.json").is_file()]
        if sibling_runs:
            logger.warning(
                "%s contains both a top-level result.json and %d run-shaped subdirectory(ies); "
                "using the top-level only — point at one of the subdirectories or the parent dir explicitly to disambiguate",
                path,
                len(sibling_runs),
            )
        task = _load_task(direct_result)
        return UsageReport(task=task)

    # Treat path as a nat-jobs/ tree.
    children = sorted(c for c in path.iterdir() if c.is_dir())
    runs: list[TaskUsage] = []
    skipped = 0
    unparseable = 0
    for child in children:
        candidate = child / "result.json"
        if not candidate.is_file():
            logger.warning("skipping %s — no result.json", child)
            skipped += 1
            continue
        try:
            runs.append(_load_task(candidate))
        except UsageParseError as exc:
            # Skip + count + warn rather than aborting N-1 valid sibling runs
            # on a single truncated/malformed result.json.
            logger.warning("skipping %s — %s", candidate, exc)
            unparseable += 1

    if not runs:
        raise UsageParseError(
            f"no parseable result.json files found under {path} (skipped: {skipped}, unparseable: {unparseable})"
        )

    runs.sort(key=lambda r: r.timestamp)

    # A single canonical "missing usage" predicate drives both totals-gating
    # and the null-runs counter, so they cannot disagree.  Three independent
    # field-by-field tests would be a footgun (a run with prompt=null but
    # total!=null would null prompt_total while leaving null_token_runs at 0).
    def _missing(r: TaskUsage) -> bool:
        return r.prompt_tokens is None or r.completion_tokens is None or r.total_tokens is None

    null_count = sum(1 for r in runs if _missing(r))

    # Totals are populated only when the batch is fully complete: every
    # parsed run has all three token fields, *and* no sibling child was
    # skipped (no result.json) or failed to decode.  Otherwise downstream
    # consumers risk treating a partial sum as a real total.
    if null_count == 0 and skipped == 0 and unparseable == 0:
        prompt_total: int | None = sum(r.prompt_tokens for r in runs if r.prompt_tokens is not None)
        completion_total: int | None = sum(r.completion_tokens for r in runs if r.completion_tokens is not None)
        total_total: int | None = sum(r.total_tokens for r in runs if r.total_tokens is not None)
    else:
        prompt_total = completion_total = total_total = None

    return BatchUsageReport(
        runs=runs,
        prompt_tokens_total=prompt_total,
        completion_tokens_total=completion_total,
        total_tokens_total=total_total,
        compute_units_total=None,  # populated by the CLI after scoring each run
        null_token_runs=null_count,
        skipped_runs=skipped,
        unparseable_runs=unparseable,
    )


def _load_task(result_json: Path) -> TaskUsage:
    """Read a single ``result.json`` and lift it into a :class:`TaskUsage`.

    Defensive about input shape.  Failure modes are converted to
    :class:`UsageParseError` so the CLI's catch tuple actually catches them
    (and the batch loop counts them in ``unparseable_runs`` rather than
    aborting N-1 valid sibling runs):

    - the file can't be read (chmod 000, broken symlink, IO error) or its
      bytes aren't UTF-8 — both raise ``OSError`` / ``UnicodeDecodeError``
      from ``read_text``;
    - JSON that doesn't decode at all (``json.loads`` raises);
    - JSON that decodes to something other than an object (``null``,
      ``[]``, ``"string"``, ``42``) — would otherwise raise
      ``AttributeError`` from ``data.get(...)``;
    - JSON object that contains none of the recognized result.json keys —
      would otherwise produce a default-filled :class:`TaskUsage` from an
      unrelated config / log file (the silent-garbage failure mode);
    - JSON object that fails Pydantic validation (e.g., ``metrics`` is a
      list, or a token field is non-coercible).
    """
    try:
        text = result_json.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise UsageParseError(f"{result_json}: cannot read file ({exc})") from exc
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UsageParseError(f"{result_json}: invalid JSON ({exc})") from exc

    if not isinstance(data, dict):
        raise UsageParseError(f"{result_json}: expected JSON object, got {type(data).__name__}")

    missing = _REQUIRED_KEYS - data.keys()
    if missing:
        raise UsageParseError(f"{result_json}: not a result.json — missing required key(s) {sorted(missing)}")

    metrics = data.get("metrics")
    if metrics is None:
        metrics = {}
    if not isinstance(metrics, dict):
        raise UsageParseError(f"{result_json}: 'metrics' must be a JSON object, got {type(metrics).__name__}")

    try:
        return TaskUsage(
            task=data["task"],
            timestamp=data.get("timestamp", ""),
            image=data.get("image"),
            reward=data.get("reward"),
            build_status=data.get("build"),
            agent_status=data.get("agent"),
            verify_status=data.get("verify"),
            prompt_tokens=metrics.get("prompt_tokens"),
            completion_tokens=metrics.get("completion_tokens"),
            total_tokens=metrics.get("total_tokens"),
            compute_units=None,
            source_dir=str(result_json.parent.resolve()),
        )
    except ValidationError as exc:
        raise UsageParseError(f"{result_json}: schema mismatch — {exc}") from exc
