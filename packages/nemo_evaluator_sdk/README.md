# NeMo Evaluator SDK

## Quickstart

```python
from nemo_evaluator_sdk import evaluate

result = evaluate(
    dataset="data/eval.jsonl",
    metric="exact_match",
    reference="{{ expected }}",
    candidate="{{ prediction }}",
)

result.print_summary()
rows_df = result.to_pandas()
aggregate_df = result.to_pandas(view="aggregate")
```

`evaluate(...)` is the recommended product-level API for scripts and notebooks. It accepts:
- inline rows
- `DatasetRows`
- `pyarrow.Table`
- a local file path
- a local directory path plus an optional `pattern`

The returned `OfflineEvaluationResult` supports:
- `print_summary()`
- `format_summary()`
- `to_records()`
- `to_table()`
- `to_pandas()`

Pandas conversion is optional. Install `nemo-evaluator-sdk[pandas]` to use `to_pandas()`.

Offline evaluation uses each dataset row as both `item` and `sample`. In practice,
that means templates should usually read directly from the row, for example
`{{item.answer}}` and `{{item.model_output}}`.

## Advanced Usage

If you want direct control over metric construction or async execution, the low-level APIs remain available:

```python
from nemo_evaluator_sdk import ExactMatchMetric, evaluate_offline_sync

metric = ExactMatchMetric.from_template(
    reference="{{item.expected}}",
    candidate="{{item.prediction}}",
)

result = evaluate_offline_sync(metric=metric, dataset=[{"expected": "4", "prediction": "4"}])
```
