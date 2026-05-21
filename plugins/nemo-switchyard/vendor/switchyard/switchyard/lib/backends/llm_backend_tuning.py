# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shared tuning knobs applied by LLM backends before the upstream call.

Two cross-cutting concerns land in one small module:

- :class:`ReasoningEffort` — cross-format enum (``DISABLED`` / ``LOW``
  / ``MEDIUM`` / ``HIGH`` / ``XHIGH`` / ``MAX``).  One knob; each
  backend translates it to its own wire shape.

  * :class:`OpenAILLMBackend` writes
    ``body["reasoning_effort"] = value`` for ``LOW / MEDIUM / HIGH``
    and rejects ``XHIGH`` / ``MAX`` at construction time (those
    levels are Anthropic-only — OpenAI's ``reasoning_effort`` tops
    out at ``"high"``).
  * :class:`AnthropicNativeLLMBackend` enables Anthropic's adaptive
    thinking + output-config effort pattern:
    ``body["thinking"] = {"type": "adaptive"}`` +
    ``body["output_config"] = {"effort": value}``.  All five
    non-``DISABLED`` levels are valid on Claude Opus 4.6 / Sonnet 4.6
    / Opus 4.7 (``XHIGH`` is Opus 4.7 only — older models in this
    range 400 at request time).

- :class:`LLMBackendTuning` — frozen dataclass holding the knobs a
  concrete :class:`LLMBackend` applies to every request: a
  ``max_output_tokens`` fallback for providers (e.g. NVIDIA NIM) that
  otherwise default to absurdly small completion budgets, plus the
  reasoning-effort level above.

The ``reasoning_effort`` field is nullable so ``None`` means "don't
touch the body's reasoning fields" — a distinct state from
:attr:`ReasoningEffort.DISABLED` which actively forces thinking off.
Similarly ``max_output_tokens`` only injects a default when the
client's body carries neither ``max_tokens`` nor
``max_completion_tokens``; a client-supplied cap is never
overridden.

See ``docs/random_routing_v2_design.md`` §3.6 for the per-backend
mapping tables and NVIDIA Inference Hub examples.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReasoningEffort(str, Enum):
    """Cross-format reasoning intensity.

    Inherits :class:`str` so values survive JSON / YAML round-trips
    with zero ceremony — operators can spell the field as
    ``reasoning_effort: "high"`` in config files.

    Values match the wire strings used by both OpenAI
    (``reasoning_effort``) and Anthropic (``output_config.effort``)
    so no translation table is needed — each backend just passes the
    enum's ``.value`` through.

    Level support matrix:

    * :attr:`DISABLED` — turns thinking off explicitly.  Both
      backends support this.
    * :attr:`LOW` / :attr:`MEDIUM` / :attr:`HIGH` — both backends
      support these.
    * :attr:`XHIGH` — Anthropic Opus 4.7 only.
      :class:`OpenAILLMBackend` rejects this at construction time.
    * :attr:`MAX` — Anthropic Opus 4.6 / Opus 4.7 / Sonnet 4.6.
      :class:`OpenAILLMBackend` rejects this at construction time.
    """

    DISABLED = "disabled"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    XHIGH = "xhigh"
    MAX = "max"


#: ``ReasoningEffort`` values :class:`OpenAILLMBackend` will not
#: accept.  Kept as a module-level constant so the backend's
#: construction-time validator and its tests can reference the same
#: source of truth.
OPENAI_UNSUPPORTED_REASONING_EFFORTS: frozenset[ReasoningEffort] = frozenset({
    ReasoningEffort.XHIGH,
    ReasoningEffort.MAX,
})


@dataclass(frozen=True)
class LLMBackendTuning:
    """Per-backend tuning knobs applied on every request.

    Attributes:
        max_output_tokens: Fallback max completion tokens.  When set
            and the client's body carries neither ``max_tokens`` nor
            ``max_completion_tokens``, the backend injects this value
            as ``max_tokens``.  Motivated by NVIDIA NIM defaulting to
            32-token completions when the field is absent.  A
            client-supplied cap is **never** overridden.  ``None``
            (default) disables the fallback.
        reasoning_effort: Cross-format reasoning intensity.

            * ``None`` (default) — passthrough.  The backend does not
              touch the body's reasoning fields; whatever the client
              sent flows through.  (``OpenAILLMBackend`` in this
              state forwards ``reasoning_effort`` as-is;
              ``AnthropicNativeLLMBackend`` still strips
              ``reasoning_effort`` because that key is not a valid
              Anthropic field, but leaves ``body["thinking"]`` and
              ``body["output_config"]`` alone.)
            * :attr:`ReasoningEffort.DISABLED` — strip reasoning
              fields; force thinking off.
            * :attr:`ReasoningEffort.LOW` /
              :attr:`ReasoningEffort.MEDIUM` /
              :attr:`ReasoningEffort.HIGH` — force to that level.
              Both backends accept these.
            * :attr:`ReasoningEffort.XHIGH` /
              :attr:`ReasoningEffort.MAX` — Anthropic-only.  Pairing
              with :class:`OpenAILLMBackend` raises
              :class:`ValueError` at construction time.
    """

    max_output_tokens: int | None = None
    reasoning_effort: ReasoningEffort | None = None
