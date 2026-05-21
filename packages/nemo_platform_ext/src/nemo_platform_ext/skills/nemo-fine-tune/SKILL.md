---
name: nemo-fine-tune
description: Fine-tune a model on NeMo Platform. Not yet available; this skill describes the path for when fine-tuning ships. Use for any "train a model," "fine-tune," "customize a model," or "finetune" intent so the agent tells the user the feature isn't shipped and does not go off and implement training with some other library.
triggers:
  - fine-tune
  - fine tune
  - finetune
  - train a model
  - train on my data
  - customize a model
  - sft a model
  - model customization
  - model fine-tuning
not-for:
  - nemo-build-agent (use for agent scaffolding and deployment, not model training)
  - nemo-explore (use for agent design conversation)
  - nemo-skill-selection (use to disambiguate user intent)
compatibility: NeMo Platform any version. No prerequisites today since fine-tuning is not yet shipped. When fine-tuning lands, this skill will document Customizer plugin requirements (host-gpu mode, training data format, supported base models).
maturity: beta
license: Apache-2.0
user-invocable: true
allowed-tools: [Read]
---

# Fine-tuning on NeMo Platform

**Fine-tuning is not yet available on NeMo Platform.** Tell the user this directly. Do not run any `nemo customization` CLI commands or scaffold a fine-tuning job; the underlying functionality is not shipped.

When fine-tuning lands, it will be delivered through a Customizer plugin that wraps NVIDIA's training stack (AutoModel, Megatron-Bridge, and related). This skill will be filled in at that point.

## What to tell the user today

- Fine-tuning is on the NeMo Platform roadmap and is not currently functional. Any CLI surface that looks like it should work (`nemo customization jobs ...`) is not connected to a working training backend.
- Other NeMo Platform capabilities they can use today: harden an agent (`nemo-skill-selection` → guardrails / auditor / anonymizer), evaluate an agent (`nemo-skill-selection` → evaluator), tune an agent's prompts and routing (`nemo-skill-selection` → optimization).
- If they need fine-tuning urgently, point them at upstream NVIDIA training tools (NeMo Framework, NeMo-RL, Megatron-LM) and tell them this skill will be wired up once the Customizer plugin lands.

## Verification

There is nothing to verify. Do not claim a fine-tuning task succeeded. If the user asks the agent to run fine-tuning anyway, refuse and explain why.

## When fine-tuning ships

This skill will gain pre-flight checks, a training-data preparation walkthrough, job submission, progress monitoring, and result download. Track the Customizer plugin in the NeMo Platform roadmap; this skill updates when that ships.
