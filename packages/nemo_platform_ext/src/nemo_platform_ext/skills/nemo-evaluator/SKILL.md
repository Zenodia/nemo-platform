---
name: nemo-evaluator
description: >
  NeMo evaluator CLI reference for metrics, evaluations, metric jobs, and benchmarks.
  Use when the task involves evaluation metrics, string-check, llm-judge, tool-calling
  metrics, sync/async evaluations, benchmark jobs, or `nemo evaluation` CLI commands.
user-invocable: true
allowed-tools: Bash, Read, Grep
---

# NeMo Evaluator CLI Reference

## Environment

- **CLI path**: `/app/.venv/bin/nemo`
- **API server**: `http://localhost:8080` (default)

## Metric Commands

```bash
# Create a string-check metric
nemo evaluation metrics create <name> \
  --type string-check \
  --params '{"field": "output", "expected_field": "expected", "operation": "equals"}' \
  --workspace <workspace>

# Create a metric from a JSON file (for complex types like llm-judge)
nemo evaluation metrics create <name> \
  --workspace <workspace> \
  --input-file <path-to-json>

# List metrics
nemo evaluation metrics list --workspace <workspace>

# Get a metric
nemo evaluation metrics get <name> --workspace <workspace>
```

## Sync Evaluation Commands

```bash
# Run sync evaluation with inline data
nemo evaluation metrics run \
  --name <metric_name> \
  --data '<jsonl_rows>' \
  --workspace <workspace>
```

Each row in `--data` is a JSON object with fields the metric references.

## Async Metric Job Commands

```bash
# Create an async metric job
nemo evaluation metric-jobs create <job_name> \
  --metric-name <metric_name> \
  --dataset-fileset <fileset_name> \
  --workspace <workspace>

# Check job status
nemo evaluation metric-jobs get <job_name> --workspace <workspace>

# List jobs
nemo evaluation metric-jobs list --workspace <workspace>
```

**Note**: Jobs may stay in "created" status if the job controller is not running — that is expected.

## Benchmark Commands

```bash
# List system benchmarks (from system workspace)
nemo evaluation benchmarks list --workspace system

# Get benchmark details
nemo evaluation benchmarks get <name> --workspace system

# Create a benchmark eval job
nemo evaluation benchmark-jobs create <job_name> \
  --benchmark <benchmark_spec_json> \
  --workspace <workspace>

# Check benchmark job status
nemo evaluation benchmark-jobs get <job_name> --workspace <workspace>
```

## Metric Types

### string-check
Compares fields using an operation (equals, contains, etc.):
```json
{"field": "output", "expected_field": "expected", "operation": "equals"}
```
Dataset rows need `output` and `expected` fields.

### llm-judge
Uses an LLM to score responses. Create via `--input-file` with this JSON structure:
```json
{
  "type": "llm-judge",
  "name": "quality-judge",
  "model": {
    "url": "https://integrate.api.nvidia.com/v1",
    "name": "openai/gpt-oss-20b",
    "format": "openai",
    "api_key_secret": "<secret-name>"
  },
  "scores": [
    {
      "name": "relevance",
      "description": "Relevance score from 1 to 5",
      "minimum": 1,
      "maximum": 5,
      "parser": {"type": "json", "json_path": "relevance"}
    }
  ],
  "prompt_template": {
    "messages": [
      {"role": "system", "content": "Rate the response on relevance 1-5. Return JSON: {\"relevance\": <score>}"},
      {"role": "user", "content": "Question: {{item.input}}\nResponse: {{item.output}}"}
    ]
  }
}
```
Requires a secret with the API key (use `nemo-secrets` skill).

### zero-config llm-judge
Same as llm-judge but without `prompt_template` and score `parser` — the system auto-generates them. Just provide `scores` with `name`, `description`, `minimum`, `maximum`, and a rubric.

### tool-calling
Evaluates function call accuracy. Dataset rows need `messages`, `tools`, `expected_tool_calls`, `response` fields in OpenAI format.

## Typical Workflow

1. Create workspace: `nemo workspaces create <ws>`
2. Upload dataset: create fileset + upload JSONL file (use `nemo-files` skill)
3. Create metric (string-check, llm-judge, etc.)
4. Run sync eval with inline data to test
5. Create async metric job against the uploaded dataset
6. Check job status
