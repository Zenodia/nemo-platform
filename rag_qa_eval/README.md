# RAG QA evaluation — toy example implemented with the NeMo Evaluator SDK

This example is a toy example demonstrating how to use NeMo Evaluator with LLM-as-judge style flow into a
reproducible, script-based evaluation run.

## What part of NeMo Platform this demonstrates

This example exercises the **NeMo Evaluator SDK** (`nemo_evaluator_sdk`) in
**local / offline mode** — no running platform services required.

Specifically it shows:

| SDK concept | Where used |
|---|---|
| `Evaluator.run_sync()` | Top-level entry point for a synchronous benchmark run |
| `RunConfigOnlineModel` | Controls parallelism, inference params, and retry behaviour |
| Online generation pipeline | The SDK calls the target model, collects responses, then fans them out to metrics |
| `BLEUMetric` | Deterministic n-gram overlap score (no model call) |
| `LLMJudgeMetric` + `JSONScoreParser` | LLM-as-judge scoring with a structured JSON rubric |
| `Model` + `InferenceParams` | Model endpoint and generation parameter configuration |
| `RangeScore` / `api_key_secret` | Score schema and secret resolution from env vars |

The script does **not** need `nemo services run` or any platform daemon. It
calls the NVIDIA API Catalog directly, so the only runtime dependency is a
valid `NVIDIA_API_KEY`.

## What the evaluation does

Each row in `qa_eval.jsonl` carries a pre-retrieved `retrieved_contexts` field,
so there is no live retrieval step. The pipeline:

1. **Generates** an answer by feeding `user_input` + `retrieved_contexts` into
   the naive RAG prompt from the notebook (online call to the target model).
2. **Scores** the result with three metrics that mirror the notebook's judges:

| Notebook step | NeMo Evaluator metric | What it measures |
|---|---|---|
| `ragas BleuScore(response, reference)` | `BLEUMetric` | n-gram overlap of generated answer vs gold `reference` |
| custom 0/2/4 `score_relevance(query, context)` | `context_relevance` (LLM judge) | does the context contain enough info to answer the question |
| (new — BLEU alone is harsh on short phrases) | `answer_correctness` (LLM judge) | semantic correctness of the answer vs gold reference |

## Dataset shape

`build_dataset.py` maps the source CSV to the JSONL fields the SDK expects:

```json
{"user_input": "<Question>", "retrieved_contexts": ["<Context>"], "reference": "<Answer>"}
```

## Prerequisites

- Python environment with `nemo-evaluator-sdk` installed (the repo `.venv`
  already has it via `uv sync`)
- `NVIDIA_API_KEY` set in your shell

## Run

```bash
# Activate the repo virtualenv
source .venv/bin/activate

# Set your API key
export NVIDIA_API_KEY="nvapi-..."

# 1. Build the dataset from the source CSV (run once)
python rag_qa_eval/build_dataset.py --limit 10

# 2. Smoke-test on the first 5 rows
python rag_qa_eval/run_eval.py --limit 5

# 3. Full run (drop --limit)
python rag_qa_eval/run_eval.py
```

## Swapping models / endpoints

`run_eval.py` defaults to the NVIDIA API Catalog. To score a model served
locally through the platform gateway, point the URL at the gateway and
override model names:

```bash
export RAG_GEN_MODEL="nvidia/llama-3.1-70b-instruct"
export RAG_JUDGE_MODEL="nvidia/llama-3.1-70b-instruct"
```

### Do not use reasoning models

**Neither `RAG_GEN_MODEL` nor `RAG_JUDGE_MODEL` may be a reasoning model
(e.g. `nemotron-super`, `nemotron-nano-omni`, or any model whose name
includes `reasoning`).**

NVIDIA reasoning models return `"content": null` in the chat completion
response, placing their output exclusively in `reasoning_content`. The
Evaluator SDK's `process_output` reads the `content` field and returns `None`
when that field is null. The evaluator then treats the model as having produced
no output:

- **Generator model** — `output_text` is absent from the sample, so `BLEUMetric`
  raises `"missing candidate field"` and refuses to score.
- **Judge model** — the LLM judge receives `None` from `process_output` and
  raises a validation error before it can parse the JSON score.

Because these metric-worker failures occur concurrently with in-flight
inference requests from other workers, Python's `asyncio.TaskGroup` cancels
those requests mid-flight. The error surfaces as `"Evaluation failed during
sample generation … Operation cancelled"` — a misleading message that obscures
the real metric-scoring failure.

This limitation will be resolved once the SDK's `process_output` falls back to
`reasoning_content` when `content` is null. Until then, use a standard
instruction-tuned model for both generation and judging.

## Remote platform job (optional)

To run as a platform-managed job instead of locally, upload the JSONL as a
fileset and reference it from a job spec:

```bash
nemo files filesets create rag-qa-eval
nemo files upload rag_qa_eval/qa_eval.jsonl rag-qa-eval
```

For remote jobs, `NVIDIA_API_KEY` must exist as a platform secret of the same
name in the job workspace.
