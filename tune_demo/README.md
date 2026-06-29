# 03-Tune toy example — Prompt Strategy Optimizer

This script demonstrates the **skill-optimization** capability of NeMo Platform
by searching over candidate prompt strategies and scoring each against a fixed
evaluation dataset.

## What part of NeMo Platform this demonstrates

| Production component | What this script does instead |
|---|---|
| NeMo skill optimizer (`nemo agents optimize-skills`) | `run_tune.py` evaluation loop |
| Evaluator service (distributed scoring) | In-process LLM-as-judge over 5 rows |
| Switchyard (runtime model routing) | Discussed in README; single model used |
| Agent YAML promotion of winning config | Printed at end of run |

### Optimization loop

```
Candidate strategies (system prompt + temperature)
        │
        ▼ for each strategy
┌───────────────────────┐
│  Run on eval dataset  │  ← fixed 5-question benchmark
└───────────────────────┘
        │
        ▼ for each response
┌───────────────────────┐
│   LLM judge (0–4)     │  ← same model, self-check pattern
└───────────────────────┘
        │
        ▼
  Average score per strategy
        │
        ▼
  Winner → promoted config
```

### Strategies compared

| Name | Approach | Temperature |
|---|---|---|
| Terse | One-sentence answer only | 0.0 |
| Explanatory | Expert assistant with examples | 0.3 |
| Structured | Fixed Answer / Why template | 0.0 |
| Chain-of-thought | Step-by-step reasoning | 0.2 |

## Prerequisites

- Python environment with `openai` installed (the repo `.venv` has it)
- `INFERENCE_API_KEY` set in your shell

## Run

```bash
source .venv/bin/activate
export INFERENCE_API_KEY="nvapi-..."

# Standard run — shows average score per strategy and the winner
python tune_demo/run_tune.py

# Verbose — prints each Q / answer / judge score
python tune_demo/run_tune.py --verbose
```

## Expected output (abbreviated)

```
================================================================
NeMo Platform — 03-Tune: Prompt Strategy Optimizer
Model      : aws/anthropic/bedrock-claude-sonnet-4-6
Strategies : 4  |  Eval dataset: 5 rows
================================================================

  Evaluating [Terse]
    avg score : 2.80 / 4.0   per-row: [3, 3, 3, 2, 3]

  Evaluating [Explanatory]
    avg score : 3.60 / 4.0   per-row: [4, 4, 3, 3, 4]

  Evaluating [Structured]
    avg score : 3.20 / 4.0   per-row: [3, 3, 4, 3, 3]

  Evaluating [Chain-of-thought]
    avg score : 3.40 / 4.0   per-row: [4, 3, 3, 4, 3]

================================================================
Rankings
================================================================
  1. Explanatory          avg=3.60/4.0 ← WINNER
  2. Chain-of-thought     avg=3.40/4.0
  3. Structured           avg=3.20/4.0
  4. Terse                avg=2.80/4.0

  Best strategy : [Explanatory]
  System prompt : 'You are a knowledgeable assistant ...'
  Temperature   : 0.3
```

## Relation to production NeMo Tuning

In production you would:

1. Run `nemo agents optimize-skills` to launch a managed optimization job.
2. The platform searches a larger strategy space and evaluates on a held-out
   dataset via the Evaluator service.
3. The winning config is automatically written back to the agent's YAML and
   can be promoted with `nemo agents deploy`.

**Switchyard** (model routing) extends this by letting the optimizer assign
*different models* to different query complexities — e.g. a small fast model
for simple factual queries, a large model only for complex reasoning — reducing
cost while preserving accuracy.
