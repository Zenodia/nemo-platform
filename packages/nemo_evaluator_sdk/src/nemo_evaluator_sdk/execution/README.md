# Execution Architecture

The execution package exposes a single public entrypoint:

- `Evaluator`
  Result-oriented API that evaluates one metric or a sequence of metrics and
  returns finished `EvaluationResult` or `BenchmarkEvaluationResult` values.

## Public Surface

- `Evaluator.run()` / `Evaluator.run_sync()`
  Evaluate one metric or many metrics and return the completed result.
- `RunConfig`
  A Pydantic config type for execution-only settings such as parallelism and
  sample limits.
- `EvaluationRequest`
  The normalized request object passed into evaluation backends.
- `EvaluationBackend`
  The protocol implemented by result-returning execution backends.

## Backend Selection

```python
# Local SDK execution
evaluator = Evaluator()
result = await evaluator.run(
    metrics=ExactMatchMetric(reference="{{item.reference}}"),
    dataset=[{"reference": "Paris", "output_text": "Paris"}],
)
```

```python
# Evaluator plugin execution through the plugin-owned SDK.
from nemo_evaluator.sdk.standalone_sdk.backend import AsyncNMPBackend

client = AsyncNeMoPlatform(workspace="default")
evaluator = Evaluator(client=AsyncNMPBackend(client.evaluator))
result = await evaluator.run(metrics=metric, dataset=data)
```

## Design Notes

- `Evaluator()` uses `LocalBackend`.
- `Evaluator(client=...)` accepts an evaluator backend object. For NeMo Platform
  execution, wrap the mounted evaluator resource in `NMPBackend` or
  `AsyncNMPBackend` from the evaluator plugin package.
- `nemo_platform` and `nemo_evaluator` are optional for local SDK evaluation.
