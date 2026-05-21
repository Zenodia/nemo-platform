# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Named :class:`RandomRoutingConfig` presets keyed by model pair.

Each preset encodes an opinionated strong/weak model pair plus its
canonical tuning (``max_output_tokens`` + ``reasoning_effort``).  A
preset name describes *which two models* — not *which workload* — so
the same pair can back Claude Code, PinchBench, SWE-bench, or any
other router-driven benchmark without name collision.

Shape mirrors
:class:`switchyard.deprecated.agents_sdk.recipes.OrchestratorRecipeFactory`:

- :attr:`RECIPES` — the canonical list of preset ids, suitable for
  ``argparse(choices=...)`` on the CLI.
- :meth:`get` — classmethod returning the factory for a given id,
  raising :class:`ValueError` with the full allowed list on a miss.
- One :func:`staticmethod` per preset returning a fully-specified
  :class:`RandomRoutingConfig`.

**Strict API** — presets fix the model pair and the per-tier
:class:`LLMBackendTuning`.  Callers may only adjust connectivity
(``api_key``, ``base_url``) and the coin bias (``strong_probability``).
Need a different model or different ``reasoning_effort``?  Drop back
to :class:`RandomRoutingConfig` and build it directly.  Rationale: a
preset's whole point is "this specific pair is the one we ship" —
every model override reopens that decision, so we force the explicit
path instead.

``strong_probability`` controls routing — higher value = more
strong-tier traffic.

Example::

    from switchyard import RandomRoutingPresets, SwitchyardRecipes

    config = RandomRoutingPresets.opus_nemotron_super(
        api_key=nvidia_api_key,
        strong_probability=0.3,
    )
    switchyard = SwitchyardRecipes.random_routing_recipe(config)
"""

from __future__ import annotations

from typing import Protocol, cast

from switchyard.lib.backends.backend_tier import (
    BackendFormat,
    BackendTier,
)
from switchyard.lib.backends.llm_backend_tuning import (
    LLMBackendTuning,
    ReasoningEffort,
)
from switchyard.lib.factories.random_routing.factory import (
    RandomRoutingConfig,
)


class RandomRoutingPresetFactory(Protocol):
    """Callable shape every :class:`RandomRoutingPresets` factory implements.

    Pinning the signature as a :class:`Protocol` does two jobs at once:
    gives :meth:`RandomRoutingPresets.get` a type-precise return
    annotation (no ``Callable[..., ...]`` Any-escape hatch), and
    documents the preset contract in one place — every new preset must
    accept exactly these keyword-only arguments.
    """

    def __call__(
        self,
        *,
        api_key: str | None = ...,
        base_url: str = ...,
        strong_probability: float = ...,
    ) -> RandomRoutingConfig: ...

# All shipping presets route through NVIDIA Inference Hub's
# OpenAI-compatible endpoint — callers override with ``base_url=``
# when pointing at a different gateway.
_INFERENCE_HUB_BASE_URL = "https://inference-api.nvidia.com/v1"

# Canonical Inference Hub model strings.  Anthropic / Moonshot /
# MiniMax / Nemotron models are routed without the legacy ``openai/``
# prefix — the Inference Hub gateway accepts the
# ``<cloud>/<org>/<model>`` form directly for these providers, and our
# API key is provisioned only for that "default-models" group.  Using
# the ``openai/<...>`` prefix on a Nemotron / MiniMax / Kimi model
# triggers ``key_model_access_denied`` (verified 2026-04-27 against
# ``openai/nvidia/nvidia/nemotron-3-super-v3``).  GPT-5.2 still carries
# the prefix because OpenAI-native model strings on the hub are
# routed through a different access group.  ``core/cost_estimator.py``
# keys cover both forms for back-compat.
# Bedrock-hosted Claude Opus.  Used by every shipping preset except
# :meth:`opus_kimi` (which routes via Azure to dodge Bedrock's
# ``toolSpec.name`` cap — see the Azure constant below).  Bedrock is
# where pricing entries in ``core/cost_estimator.py`` live and where
# most Inference Hub benchmark tooling expects Opus to land.
#
# 4.6 vs 4.7 split — we ship both versions as parallel presets rather
# than replacing 4.6 with 4.7 because PinchBench / SWE-bench tuning
# runs are built around 4.6 (see :meth:`opus_nemotron_super`'s
# docstring); ``*_47_*`` variants exist for callers who want the
# newer generation at the cost of re-validating the routing sweet
# spot.  Drop the 4.6 constants + presets once 4.7 benchmark history
# catches up.
_MODEL_OPUS_4_6_BEDROCK = "aws/anthropic/bedrock-claude-opus-4-6"
_MODEL_OPUS_4_7_BEDROCK = "aws/anthropic/bedrock-claude-opus-4-7"
# Azure-hosted Claude Opus 4.6, used by :meth:`opus_kimi`.  AWS
# Bedrock caps ``toolSpec.name`` at 64 characters; Claude Code
# auto-injects MCP tool names (``mcp__<server>__<tool>``) that
# routinely breach that limit, producing ``BedrockException`` 400s
# mid-session.  The Azure passthrough on NVIDIA Inference Hub
# doesn't enforce that cap, so routing Opus via Azure keeps
# ``opus_kimi`` usable as the default Claude Code preset without a
# tool-name rewriter in the chain.  **No Azure 4.7 exists today** —
# Inference Hub only ships 4.7 via Bedrock, so the ``opus_47_kimi``
# preset stays on Bedrock and callers hitting the MCP cap have to
# fall back to ``opus_kimi`` (4.6 Azure) for Claude Code workloads.
# Pricing matches Bedrock Opus 4.6 (see ``core/cost_estimator.py``).
_MODEL_OPUS_4_6_AZURE = "azure/anthropic/claude-opus-4-6"
_MODEL_GPT_5_2 = "openai/openai/openai/gpt-5.2"
_MODEL_NEMOTRON_SUPER_V3 = "nvidia/nvidia/nemotron-3-super-v3"
_MODEL_KIMI_K2_6 = "nvidia/moonshotai/kimi-k2.6"
_MODEL_MINIMAX_M2_7 = "nvidia/minimaxai/minimax-m2.7"

# Canonical per-tier output budget.  Matches
# ``switchyard random-routing`` CLI defaults.  Servers clamp
# to the model's real ceiling so oversizing is safe **for most
# models**; Nemotron is the documented exception (see
# :data:`_NEMOTRON_MAX_OUTPUT_TOKENS`).  Undersizing silently truncates
# long completions mid-generation.
_DEFAULT_MAX_OUTPUT_TOKENS = 128_000

# Nemotron Super v3's API enforces ``prompt_tokens + max_tokens ≤
# context_window (131_072)`` strictly — passing 128k as max_tokens
# leaves only 3,072 tokens for the prompt, which terminus-2 / Claude
# Code blow past within a few turns.  Verified 2026-04-27 with a
# 400 ``BadRequestError`` from the hub:
#
#     "You passed 3073 input tokens and requested 128000 output
#      tokens. However, the model's context length is only 131072
#      tokens, resulting in a maximum input length of 3072 tokens."
#
# 8,192 leaves ~123k for the prompt — plenty for terminus-2's
# JSON-schema responses and even very long agent transcripts.  Bump
# higher only if you measure single-turn output truncation; lower
# only if you're chasing strict latency / cost on per-turn output.
# Other models (Opus on Bedrock, MiniMax, Kimi) treat ``max_tokens``
# as a generation cap that fits inside the remaining context window
# rather than a strict prompt+output sum, so they don't need this.
_NEMOTRON_MAX_OUTPUT_TOKENS = 8_192


def _tuning_reasoning_high() -> LLMBackendTuning:
    """Standard tuning for reasoning-capable models.

    Single helper shared across presets so the canonical "high reasoning,
    128k output budget" choice lives in exactly one place.  When we add
    a preset that needs different defaults, that preset inlines its own
    :class:`LLMBackendTuning` construction instead of adding parameters
    to this helper (keeps each preset's invariants readable inline).
    """
    return LLMBackendTuning(
        max_output_tokens=_DEFAULT_MAX_OUTPUT_TOKENS,
        reasoning_effort=ReasoningEffort.HIGH,
    )


def _tuning_nemotron() -> LLMBackendTuning:
    """Tuning for Nemotron Super v3 — same reasoning, smaller output budget.

    Nemotron's strict ``prompt + max_tokens ≤ context`` constraint
    (see :data:`_NEMOTRON_MAX_OUTPUT_TOKENS`) means the canonical 128k
    fallback used by :func:`_tuning_reasoning_high` rejects nearly
    every multi-turn request.  Reasoning effort stays at
    :attr:`ReasoningEffort.HIGH` because Nemotron actually honours the
    field (~64% reasoning reduction at ``DISABLED`` vs ``HIGH``,
    measured 2026-04-25 via direct hub probes).
    """
    return LLMBackendTuning(
        max_output_tokens=_NEMOTRON_MAX_OUTPUT_TOKENS,
        reasoning_effort=ReasoningEffort.HIGH,
    )


class RandomRoutingPresets:
    """Factory of pre-built :class:`RandomRoutingConfig`s keyed by model pair.

    Each preset is a named strong+weak pair with fixed per-tier tuning.
    Callers vary only the per-deployment knobs (``api_key``,
    ``base_url``, ``strong_probability``); the model identities and
    reasoning/output budgets are part of the preset's identity.

    Example::

        config = RandomRoutingPresets.opus_nemotron_super(
            api_key="...",
            strong_probability=0.5,
        )

        # Dispatch by id (CLI / config-driven workflows):
        factory = RandomRoutingPresets.get("opus_nemotron_super")
        config = factory(api_key="...", strong_probability=0.5)
    """

    #: Canonical preset ids.  Kept as a class attribute so CLI parsers
    #: can use ``argparse(choices=RandomRoutingPresets.RECIPES)`` and
    #: help text auto-lists the available presets.  Presets are named
    #: by their model pair (not by workload) so the same pair can
    #: back Claude Code, PinchBench, SWE-bench, etc. without
    #: workload-specific aliases.
    RECIPES: list[str] = [
        "opus_nemotron_super",
        "gpt5_nemotron_super",
        "opus_kimi",
        "opus_minimax",
        "opus_47_nemotron_super",
        "opus_47_kimi",
        "opus_47_minimax",
    ]

    @classmethod
    def get(cls, recipe_id: str) -> RandomRoutingPresetFactory:
        """Return the factory method for *recipe_id*.

        Raises:
            ValueError: If *recipe_id* is not in :attr:`RECIPES`.  The
                error lists every allowed name so mistyped ids
                self-document their fix.
        """
        if recipe_id not in cls.RECIPES:
            raise ValueError(
                f"Unknown random-routing preset {recipe_id!r}. "
                f"Available: {cls.RECIPES}"
            )
        # Every RECIPES entry names a ``@staticmethod`` on this class,
        # so ``getattr`` resolves to the factory callable.  ``cast``
        # narrows the :class:`Any` that ``getattr`` produces back to
        # the shared :class:`RandomRoutingPresetFactory` signature —
        # all presets implement it (verified by
        # :class:`TestStrictness`'s kwargs-only tests).
        return cast(RandomRoutingPresetFactory, getattr(cls, recipe_id))

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------

    @staticmethod
    def opus_nemotron_super(
        *,
        api_key: str | None = None,
        base_url: str = _INFERENCE_HUB_BASE_URL,
        strong_probability: float = 0.5,
    ) -> RandomRoutingConfig:
        """Claude Opus 4.6 (strong) + Nemotron-3 Super v3 (weak).

        The flagship Inference Hub pair — strong-signal reasoning from
        Opus for multi-step work, cheap reasoning from Nemotron for
        straightforward calls.  native upgrade of the legacy
        :meth:`NemoSwitchyardRecipes.claude_code_recipe` at a 50/50
        split.  PinchBench on the original Opus 4.6 + Nemotron pair
        showed balanced routing matching all-strong accuracy, which is
        why this preset stays on 4.6 rather than chasing the latest
        point release.

        Tuning: both tiers use :attr:`ReasoningEffort.HIGH` with a
        128k ``max_output_tokens`` fallback.  Coding-heavy workloads
        benefit from extra thinking tokens; Nemotron handles ``high``
        natively so there's no translation loss on the weak tier.
        """
        return RandomRoutingConfig(
            strong=BackendTier(
                model=_MODEL_OPUS_4_6_BEDROCK,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            weak=BackendTier(
                model=_MODEL_NEMOTRON_SUPER_V3,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_nemotron(),
            ),
            strong_probability=strong_probability,
        )

    @staticmethod
    def gpt5_nemotron_super(
        *,
        api_key: str | None = None,
        base_url: str = _INFERENCE_HUB_BASE_URL,
        strong_probability: float = 0.5,
    ) -> RandomRoutingConfig:
        """GPT-5.2 (strong) + Nemotron-3 Super v3 (weak).

        Same weak tier as :meth:`opus_nemotron_super` but swaps Opus
        for GPT-5.2 on the strong side.  Matches the default
        strong+weak pair in the legacy
        :meth:`NemoSwitchyardRecipes.default_routellm_recipe` and the
        CLI example in ``switchyard random-routing``'s
        docstring.

        Tuning: both tiers use :attr:`ReasoningEffort.HIGH` with a
        128k ``max_output_tokens`` fallback.
        """
        return RandomRoutingConfig(
            strong=BackendTier(
                model=_MODEL_GPT_5_2,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            weak=BackendTier(
                model=_MODEL_NEMOTRON_SUPER_V3,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_nemotron(),
            ),
            strong_probability=strong_probability,
        )

    @staticmethod
    def opus_kimi(
        *,
        api_key: str | None = None,
        base_url: str = _INFERENCE_HUB_BASE_URL,
        strong_probability: float = 0.5,
    ) -> RandomRoutingConfig:
        """Claude Opus 4.6 via Azure (strong) + Moonshot Kimi K2.6 (weak).

        Moonshot-weak-tier alternative to :meth:`opus_nemotron_super`
        — useful when Kimi's training mix better matches your
        workload's prompt style or language coverage than Nemotron's.

        Strong-tier model routes through the **Azure** Anthropic
        deployment (``azure/anthropic/claude-opus-4-6``) rather than
        AWS Bedrock.  AWS Bedrock caps ``toolSpec.name`` at 64
        characters, and Claude Code's MCP bridge auto-injects tool
        names shaped like ``mcp__<server>__<tool>`` that routinely
        exceed that limit (e.g. `plugin-microsoft-docs` ships
        ``mcp__plugin_microsoft_docs_microsoft_learn__microsoft_code_sample_search``
        at 72 characters).  Azure's passthrough doesn't enforce the
        64-char cap, so the preset stays usable as the default
        Claude Code pair without a request-side tool-name rewriter.
        The sister presets (``opus_nemotron_super``, ``opus_minimax``)
        stay on Bedrock/4.7 because their typical workloads (PinchBench,
        SWE-bench) don't hit Claude Code's MCP tool-name path.

        Tuning: both tiers use :attr:`ReasoningEffort.HIGH` with a
        128k ``max_output_tokens`` fallback.  Kimi K2.6 supports
        reasoning natively, so the weak tier gets real thinking
        tokens on multi-step prompts rather than a forced strip.
        """
        return RandomRoutingConfig(
            strong=BackendTier(
                model=_MODEL_OPUS_4_6_AZURE,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            weak=BackendTier(
                model=_MODEL_KIMI_K2_6,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            strong_probability=strong_probability,
        )

    @staticmethod
    def opus_minimax(
        *,
        api_key: str | None = None,
        base_url: str = _INFERENCE_HUB_BASE_URL,
        strong_probability: float = 0.5,
    ) -> RandomRoutingConfig:
        """Claude Opus 4.6 (strong) + MiniMax M2.7 (weak).

        Same Opus 4.6 strong tier as :meth:`opus_nemotron_super`;
        swaps Nemotron for MiniMax M2.7 on the weak side.  Use when
        MiniMax has better coverage for your workload's languages or
        prompt styles, or when you want to compare two reasoning-
        capable weak tiers side-by-side at the same split.  Unlike
        :meth:`opus_kimi` the strong tier stays on AWS Bedrock —
        benchmark workloads on this pair don't bump into the
        ``toolSpec.name`` length cap that motivates the Azure split
        for Claude Code.

        Tuning: both tiers use :attr:`ReasoningEffort.HIGH` with a
        128k ``max_output_tokens`` fallback.  MiniMax M2.7 supports
        reasoning natively so the weak tier contributes real thinking
        tokens, not a forced strip.
        """
        return RandomRoutingConfig(
            strong=BackendTier(
                model=_MODEL_OPUS_4_6_BEDROCK,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            weak=BackendTier(
                model=_MODEL_MINIMAX_M2_7,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            strong_probability=strong_probability,
        )

    # ------------------------------------------------------------------
    # Opus 4.7 variants
    # ------------------------------------------------------------------
    #
    # Parallel to the 4.6 presets above — same weak tiers, same
    # Bedrock/Azure split rationale, only the strong-tier version
    # changes.  Kept as separate factories (not a ``version=`` kwarg
    # on the 4.6 presets) because each preset's whole point is
    # "this specific pair is the one we ship"; parameterising the
    # version would reopen that decision on every call.

    @staticmethod
    def opus_47_nemotron_super(
        *,
        api_key: str | None = None,
        base_url: str = _INFERENCE_HUB_BASE_URL,
        strong_probability: float = 0.5,
    ) -> RandomRoutingConfig:
        """Claude Opus 4.7 (strong) + Nemotron-3 Super v3 (weak).

        4.7-on-Bedrock counterpart to :meth:`opus_nemotron_super`.
        Pick this when you want the newer Opus generation and are
        willing to re-validate the routing sweet spot — PinchBench /
        SWE-bench balance numbers on this pair are less established
        than the 4.6 variant, which is why we still ship both.

        Strong tier uses :attr:`BackendFormat.ANTHROPIC` — Opus 4.7
        on Bedrock rejects ``thinking: {type: "enabled"}`` (the
        shape LiteLLM emits when it sees ``reasoning_effort`` on the
        Chat Completions path) and requires ``thinking.type=adaptive``
        + ``output_config.effort``.  :class:`AnthropicNativeLLMBackend`
        writes exactly that shape, so we hit Inference Hub's
        ``/v1/messages`` endpoint for Opus 4.7 while Nemotron stays
        on the OpenAI Chat Completions path.

        Tuning: both tiers use :attr:`ReasoningEffort.HIGH` with a
        128k ``max_output_tokens`` fallback.  Callers wanting Opus
        4.7's ``XHIGH`` reasoning effort should drop to
        :class:`RandomRoutingConfig` directly — presets fix the
        tuning so a version bump doesn't silently change reasoning
        budget.
        """
        return RandomRoutingConfig(
            strong=BackendTier(
                model=_MODEL_OPUS_4_7_BEDROCK,
                backend_format=BackendFormat.ANTHROPIC,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            weak=BackendTier(
                model=_MODEL_NEMOTRON_SUPER_V3,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_nemotron(),
            ),
            strong_probability=strong_probability,
        )

    @staticmethod
    def opus_47_kimi(
        *,
        api_key: str | None = None,
        base_url: str = _INFERENCE_HUB_BASE_URL,
        strong_probability: float = 0.5,
    ) -> RandomRoutingConfig:
        """Claude Opus 4.7 via Bedrock (strong) + Moonshot Kimi K2.6 (weak).

        4.7 counterpart to :meth:`opus_kimi` — same weak tier, same
        split knob, but strong-tier hosting is **Bedrock** rather
        than Azure because Inference Hub only ships Opus 4.7 on
        Bedrock today; no ``azure/anthropic/claude-opus-4-7`` route
        exists.

        Claude Code caveat: because Bedrock still enforces the
        64-character ``toolSpec.name`` cap (Claude Code's MCP bridge
        auto-injects tool names like
        ``mcp__<server>__<tool>`` that routinely exceed 64 chars),
        this preset will hit ``BedrockException`` 400s on long MCP
        tool names that :meth:`opus_kimi` dodges via the Azure
        route.  For Claude Code traffic with third-party MCP
        servers attached, prefer :meth:`opus_kimi` (4.6 Azure)
        until Inference Hub exposes an Azure 4.7 deployment.  The
        benchmark-focused workloads this preset is typically used
        for (PinchBench, SWE-bench) don't inject MCP tools, so the
        cap doesn't bite there.

        Strong tier uses :attr:`BackendFormat.ANTHROPIC` — Opus 4.7
        on Bedrock rejects ``thinking: {type: "enabled"}`` (the
        shape LiteLLM emits when it sees ``reasoning_effort`` on the
        Chat Completions path) and requires ``thinking.type=adaptive``
        + ``output_config.effort``.  :class:`AnthropicNativeLLMBackend`
        writes exactly that shape, so we hit Inference Hub's
        ``/v1/messages`` endpoint for Opus 4.7 while Kimi stays on
        the OpenAI Chat Completions path.

        Tuning: both tiers use :attr:`ReasoningEffort.HIGH` with a
        128k ``max_output_tokens`` fallback.  Kimi K2.6 supports
        reasoning natively so the weak tier gets real thinking
        tokens rather than a forced strip.
        """
        return RandomRoutingConfig(
            strong=BackendTier(
                model=_MODEL_OPUS_4_7_BEDROCK,
                backend_format=BackendFormat.ANTHROPIC,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            weak=BackendTier(
                model=_MODEL_KIMI_K2_6,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            strong_probability=strong_probability,
        )

    @staticmethod
    def opus_47_minimax(
        *,
        api_key: str | None = None,
        base_url: str = _INFERENCE_HUB_BASE_URL,
        strong_probability: float = 0.5,
    ) -> RandomRoutingConfig:
        """Claude Opus 4.7 (strong) + MiniMax M2.7 (weak).

        4.7-on-Bedrock counterpart to :meth:`opus_minimax`.  Stays
        on AWS Bedrock because benchmark workloads on this pair
        (PinchBench, SWE-bench) don't inject MCP tool names via
        Claude Code, so Bedrock's 64-char ``toolSpec.name`` cap
        doesn't bite.  Use when you want to compare Opus 4.7's
        routing balance against the 4.6 baseline on MiniMax-weak
        traffic.

        Strong tier uses :attr:`BackendFormat.ANTHROPIC` — Opus 4.7
        on Bedrock rejects ``thinking: {type: "enabled"}`` (the
        shape LiteLLM emits when it sees ``reasoning_effort`` on the
        Chat Completions path) and requires ``thinking.type=adaptive``
        + ``output_config.effort``.  :class:`AnthropicNativeLLMBackend`
        writes exactly that shape, so we hit Inference Hub's
        ``/v1/messages`` Anthropic-compatible endpoint for Opus 4.7
        while the weak tier keeps the OpenAI Chat Completions path.

        Tuning: both tiers use :attr:`ReasoningEffort.HIGH` with a
        128k ``max_output_tokens`` fallback.  MiniMax M2.7 supports
        reasoning natively so the weak tier contributes real
        thinking tokens.
        """
        return RandomRoutingConfig(
            strong=BackendTier(
                model=_MODEL_OPUS_4_7_BEDROCK,
                backend_format=BackendFormat.ANTHROPIC,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            weak=BackendTier(
                model=_MODEL_MINIMAX_M2_7,
                backend_format=BackendFormat.OPENAI,
                api_key=api_key,
                base_url=base_url,
                tuning=_tuning_reasoning_high(),
            ),
            strong_probability=strong_probability,
        )
