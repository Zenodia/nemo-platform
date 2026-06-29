# RAG QA evaluation (Path A) — `rag_wJudge.ipynb` + `qa_toy_example.csv`

This turns the `rag_wJudge.ipynb` RAG-with-judge flow into a reproducible
**NeMo Evaluator** run over the custom `qa_toy_example.csv`.

Each CSV row already carries its own `Context`, so there is no live NeMo
Retriever call — the context is treated as the retrieved passage. We then:

1. **Generate** an answer by feeding `Question` + `Context` into the notebook's
   naive RAG prompt (online generation against the target model).
2. **Score** the run with three metrics that mirror the notebook's judges:

| Notebook step | NeMo Evaluator metric | What it measures |
|---|---|---|
| `ragas BleuScore(response, reference)` | `BLEUMetric` | generated answer vs gold `Answer` |
| custom 0/2/4 `score_relevance(query, context)` | `ContextRelevanceMetric` (LLM judge) | does the context answer the question |
| (new, BLEU is harsh on short answers) | `AnswerAccuracyMetric` (LLM judge) | semantic correctness of the answer |

## Dataset shape

`build_dataset.py` maps the CSV to the field names RAGAS expects:

```json
{"user_input": "<Question>", "retrieved_contexts": ["<Context>"], "reference": "<Answer>"}
```

## Prerequisites

- conda env `dspy_py312`
- `nemo-evaluator-sdk` installed in that env (see below)
- `NVIDIA_API_KEY` exported in the shell

Install the SDK into `dspy_py312` (editable, from this repo):

```powershell
conda activate dspy_py312
pip install -e packages/nemo_evaluator_sdk
```

## Run (smoke test first)

```powershell
# 1. Convert a small slice
conda run -n dspy_py312 python rag_qa_eval/build_dataset.py --limit 10

# 2. Score the first 5 rows
$env:NVIDIA_API_KEY = "nvapi-..."
conda run -n dspy_py312 python rag_qa_eval/run_eval.py --limit 5
```

When the smoke test looks right, build the full dataset (drop `--limit`) and
run without `--limit`.

## Swapping models / endpoints

`run_eval.py` defaults to the NVIDIA API Catalog (matching the notebook). To
score a model served locally through the platform gateway, set the chat URL to
`http://localhost:8080/v1/chat/completions` and override model names via env:

```bash
export RAG_GEN_MODEL="nvidia/llama-3.1-70b-instruct"
export RAG_JUDGE_MODEL="nvidia/llama-3.1-70b-instruct"
```

### Do not use reasoning models

**Neither `RAG_GEN_MODEL` nor `RAG_JUDGE_MODEL` may be a reasoning model
(e.g. `nemotron-super`, `nemotron-nano-omni`, or any model whose name includes
`reasoning`).**

NVIDIA reasoning models return `"content": null` in the chat completion
response, placing their output exclusively in `reasoning_content`. The
NeMo Evaluator SDK's `process_output` function reads `content` and returns
`None` when the field is null. The evaluator then treats the model as having
produced no output:

- **Generator model** — `output_text` is absent from the sample, so BLEU
  raises `"missing candidate field"` and refuses to score.
- **Judge model** — the LLM judge receives `None` from `process_output` and
  raises a validation error before it can parse the JSON score.

Because these metric-worker failures happen concurrently with in-flight
inference requests from other produce-workers, Python's `asyncio.TaskGroup`
cancels those requests mid-flight. The cancellation surfaces as
`"Evaluation failed during sample generation … Operation cancelled"` — an
unhelpfully misleading message that hides the real metric-scoring failure.

This limitation will be lifted once the SDK's `process_output` falls back to
`reasoning_content` when `content` is null (tracked internally). Until then,
use a standard instruction-tuned model for both generation and judging.

## Remote platform job (optional)

To run as a platform-managed job instead of locally, upload the JSONL as a
fileset and reference it from a job spec:

```powershell
nemo files filesets create rag-qa-eval
nemo files upload rag_qa_eval/qa_eval.jsonl rag-qa-eval
```

For remote jobs, `NVIDIA_API_KEY` must exist as a platform secret of the same
name in the job workspace.
