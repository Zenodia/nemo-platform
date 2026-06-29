# 04-Data toy example — Synthetic Dataset Generator

This script demonstrates the **NeMo Data Designer** capability: generating
diverse, structured synthetic QA pairs from a seed document that can be
consumed directly by the 02-Evaluate pipeline.

## What part of NeMo Platform this demonstrates

| Production component | What this script does instead |
|---|---|
| NeMo Data Designer managed pipeline | `run_data_designer.py` generation loop |
| Jobs service (scale-out generation) | In-process sequential calls |
| NeMo Files service (dataset storage) | Local JSONL file |
| Diversity / quality filtering | LLM-based deduplication check |

### Generation pipeline

```
Seed document
     │
     ▼  for each persona × round
┌──────────────────────────┐
│  Generate QA pair (LLM)  │  ← persona shapes question style
└──────────────────────────┘
     │
     ▼
┌──────────────────────────┐
│  Dedup check (LLM)       │  ← reject near-duplicates
└──────────────────────────┘
     │ accepted
     ▼
  JSONL record added
     │
     ▼
synthetic_dataset.jsonl  (same schema as qa_eval.jsonl)
```

### Personas used

| Persona | Question style |
|---|---|
| curious student | Simple, direct factual questions |
| technical practitioner | How-to / architectural questions |
| product evaluator | Comparative questions (feature A vs B) |
| adversarial tester | Subtle, tricky, edge-case questions |

## Prerequisites

- Python environment with `openai` installed (the repo `.venv` has it)
- `INFERENCE_API_KEY` set in your shell

## Run

```bash
source .venv/bin/activate
export INFERENCE_API_KEY="nvapi-..."

# Default: 2 rounds × 4 personas = up to 8 records
python data_demo/run_data_designer.py

# More rounds for a larger dataset
python data_demo/run_data_designer.py --rounds 5

# Use your own domain document
python data_demo/run_data_designer.py --seed-file path/to/doc.txt

# Skip dedup check (faster)
python data_demo/run_data_designer.py --no-dedup

# Custom output path
python data_demo/run_data_designer.py --output my_eval_set.jsonl
```

## Output schema

Each line in the output JSONL matches the schema used by `rag_qa_eval/`:

```json
{
  "user_input": "What does the NeMo Evaluator measure?",
  "retrieved_contexts": ["The NeMo Evaluator runs systematic benchmarks ..."],
  "reference": "It measures model quality using deterministic metrics such as BLEU and ROUGE ...",
  "persona": "technical practitioner"
}
```

## End-to-end data → evaluate loop

The generated dataset can be fed directly into the 02-Evaluate pipeline:

```bash
# 1. Generate synthetic eval data
python data_demo/run_data_designer.py --output data_demo/synthetic_dataset.jsonl

# 2. Score it with the evaluator
python rag_qa_eval/run_eval.py --dataset data_demo/synthetic_dataset.jsonl --limit 8
```

This mirrors the production flow: Data Designer fills the Files service with
a dataset, and an Evaluator job reads from Files to benchmark the agent.

## Relation to production NeMo Data Designer

In production you would:

1. Define a pipeline spec (seed documents, personas, output schema) via the
   Data Designer UI or CLI.
2. The platform runs generation jobs at scale, deduplicates across thousands
   of examples, and filters by diversity and quality scores.
3. The finished dataset lands in the NeMo Files service, ready to be
   referenced by Evaluator or Customizer jobs.
