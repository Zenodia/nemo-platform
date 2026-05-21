# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from nemo_evaluator_sdk import inference
from nemo_evaluator_sdk.enums import MetricType
from nemo_evaluator_sdk.execution.values import EvaluationError, EvaluationPhase
from nemo_evaluator_sdk.values import (
    AggregatedMetricResult,
    AggregateRangeScore,
    DatasetRows,
    Histogram,
    Percentiles,
)
from nmp.common.jobs.constants import NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, PERSISTENT_JOB_STORAGE_PATH_ENVVAR
from nmp.evaluator.app.datasets.loader import DatasetLoadError
from nmp.evaluator.app.inference_hooks import ProgressTrackingHook
from nmp.evaluator.app.jobs.constants import (
    EVALUATION_RESULTS_AGG_SCORES_FILE_NAME,
    EVALUATION_RESULTS_ROW_SCORES_FILE_NAME,
)
from nmp.evaluator.app.values import FilesetRef, MetricJobAdapter
from nmp.evaluator.tasks.evaluate_metric.__main__ import (
    _apply_optional_fields_to_row,
    _json_default,
    _load_dataset_items,
    evaluate_metric,
    main,
    metric_evaluation_entrypoint,
    metric_evaluation_entrypoint_args,
    no_aggregated_metric_scores,
    run,
)
from pytest_mock import MockerFixture

TEST_DIR = os.path.dirname(__file__).rsplit("/", 1)[0]
INFERENCE_FAILURE_HINT = (
    "To prevent failure of evaluation from inference request failures, check the model endpoint, "
    "credentials, request timeout, and retry settings, or set params.ignore_request_failure=true "
    "to mark failed rows as NaN."
)


def _expected_inference_failure_message(row_index: int) -> str:
    return f"Row {row_index} failed inference: Simulated inference failure. {INFERENCE_FAILURE_HINT}"


@pytest.mark.asyncio
async def test_evaluate_metric(tmp_path, monkeypatch: pytest.MonkeyPatch):
    job_file = f"{TEST_DIR}/data/metric-jobs/llm-judge-offline.json"
    expected_results_file = f"{TEST_DIR}/data/metric-jobs/llm-judge-offline-results.json"
    results_dir = tmp_path / "results"
    monkeypatch.setenv(NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, job_file)
    monkeypatch.setenv(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, str(tmp_path))

    with patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.make_inference_request", new_callable=AsyncMock
    ) as make_inference_request:
        make_inference_request.return_value = {"choices": [{"message": {"content": '{"length": "short"}'}}]}
        await main(["--skip-upload-results", "true"])

    with open(expected_results_file) as f:
        expected_results = json.load(f)

    actual_results_file = Path(results_dir, EVALUATION_RESULTS_AGG_SCORES_FILE_NAME)
    with open(actual_results_file) as f:
        actual_results = json.load(f)

    assert actual_results == expected_results

    detailed_results_file = Path(results_dir, EVALUATION_RESULTS_ROW_SCORES_FILE_NAME)
    with open(detailed_results_file) as f:
        num_lines = sum(1 for line in f)
    assert num_lines == 3, "expected an evaluation for each row"


@pytest.mark.asyncio
async def test_evaluate_metric_offline_uses_shared_generated_sample_pipeline(tmp_path, mocker: MockerFixture):
    job_file = f"{TEST_DIR}/data/metric-jobs/llm-judge-offline.json"

    with open(job_file) as f:
        job = MetricJobAdapter.validate_python(json.load(f))

    pipeline_result = [
        (
            0,
            None,
            mocker.Mock(
                item={"input": "What is Python?", "output": "A programming language"},
                sample={},
            ),
        ),
        (
            1,
            None,
            mocker.Mock(
                item={"input": "Explain quantum computing", "output": "Complex physics stuff"},
                sample={},
            ),
        ),
    ]

    run_pipeline_mock = mocker.patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.run_generated_sample_scoring_pipeline",
        new_callable=AsyncMock,
        return_value=pipeline_result,
    )
    metric_mock = mocker.Mock()
    metric_mock.type = MetricType.LLM_JUDGE
    mocker.patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.new_metric",
        new_callable=AsyncMock,
        return_value=metric_mock,
    )
    new_hooks_mock = mocker.patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.inference_hooks.new_hooks",
        return_value=([], []),
    )
    finalize_mock = mocker.patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.finalize_evaluation_result",
        new_callable=AsyncMock,
        return_value=mocker.Mock(
            aggregate_scores=AggregatedMetricResult(scores=[]),
            row_scores=[],
        ),
    )

    await evaluate_metric(job, str(tmp_path))

    run_pipeline_mock.assert_awaited_once()
    new_hooks_mock.assert_called_once_with(job.params, model_format=None)
    finalize_mock.assert_awaited_once()

    assert run_pipeline_mock.await_args is not None
    pipeline = run_pipeline_mock.await_args.args[0]
    assert pipeline.rows == [
        {"input": "hi.", "output": "hello world"},
        {"input": "Are you hungry?", "output": "no"},
        {
            "input": "What is coffee?",
            "output": "a hot drink made from the roasted and ground seeds (coffee beans) of a tropical shrub.",
        },
    ]
    assert pipeline.parallelism == job.params.parallelism
    assert pipeline.target is None
    assert pipeline.prompt_template is None
    assert pipeline.metric_key == "llm-judge"


@pytest.mark.asyncio
async def test_evaluate_metric_offline_uses_string_metric_type_for_metric_key(tmp_path, mocker: MockerFixture):
    job_file = f"{TEST_DIR}/data/metric-jobs/llm-judge-offline.json"

    with open(job_file) as f:
        job = MetricJobAdapter.validate_python(json.load(f))

    run_pipeline_mock = mocker.patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.run_generated_sample_scoring_pipeline",
        new_callable=AsyncMock,
        return_value=[],
    )

    class StringMetric:
        type = "custom-metric"

    metric_mock = StringMetric()
    mocker.patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.new_metric",
        new_callable=AsyncMock,
        return_value=metric_mock,
    )
    mocker.patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.inference_hooks.new_hooks",
        return_value=([], []),
    )
    mocker.patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.finalize_evaluation_result",
        new_callable=AsyncMock,
        return_value=mocker.Mock(
            aggregate_scores=AggregatedMetricResult(scores=[]),
            row_scores=[],
        ),
    )

    await evaluate_metric(job, str(tmp_path))

    assert run_pipeline_mock.await_args is not None
    pipeline = run_pipeline_mock.await_args.args[0]
    assert pipeline.metric_key == "custom-metric"


@pytest.mark.asyncio
async def test_evaluate_metric_inference_failure_with_ignore_flag_returns_nan(tmp_path):
    """Test that inference failures return NaN scores when ignore_request_failure is True."""
    job_config = {
        "model": {
            "name": "test-model",
            "url": "http://test:8000/v1/chat/completions",
            "api_key_secret": None,
        },
        "dataset": {
            "rows": [
                {"input": "test input 1"},
                {"input": "test input 2"},
            ],
        },
        "prompt_template": {"messages": [{"role": "user", "content": "{{input}}"}]},
        "params": {
            "ignore_request_failure": True,
        },
        "metric": {
            "type": "exact-match",
            "name": "test-metric",
            "workspace": "default",
            "reference": "{{item.expected}}",
        },
    }

    job = MetricJobAdapter.validate_python(job_config)

    with patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.make_inference_request", new_callable=AsyncMock
    ) as mock_inference:
        # Simulate inference failure
        mock_inference.side_effect = Exception("Simulated inference failure")

        result = await evaluate_metric(job, str(tmp_path))

    # Verify we got results with NaN tracking
    assert len(result.scores) == 1
    score = result.scores[0]
    assert isinstance(score, AggregateRangeScore)
    assert score.name == "exact-match"
    # AggregateScore has nan_count and count directly (not nested in stats)
    assert score.nan_count == 2
    assert score.count == 0
    assert score.mean is None
    assert score.sum is None
    assert score.min is None
    assert score.max is None
    assert score.std_dev is None
    assert score.variance is None
    assert isinstance(score, AggregateRangeScore)
    assert score.percentiles is None

    with open(tmp_path / EVALUATION_RESULTS_ROW_SCORES_FILE_NAME) as f:
        rows = [json.loads(line) for line in f]

    assert [row["row_index"] for row in rows] == [0, 1]
    assert all(
        row["metric_errors"] == {"exact-match": _expected_inference_failure_message(row["row_index"])} for row in rows
    )


@pytest.mark.asyncio
async def test_evaluate_metric_inference_failure_without_ignore_flag_raises(tmp_path):
    """Test that inference failures raise exception when ignore_request_failure is False (default)."""
    job_config = {
        "model": {
            "name": "test-model",
            "url": "http://test:8000/v1/chat/completions",
            "api_key_secret": None,
        },
        "dataset": {
            "rows": [{"input": "test input"}],
        },
        "prompt_template": {"messages": [{"role": "user", "content": "{{input}}"}]},
        "metric": {
            "type": "exact-match",
            "name": "test-metric",
            "workspace": "default",
            "reference": "{{item.expected}}",
        },
    }

    job = MetricJobAdapter.validate_python(job_config)

    with patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.make_inference_request", new_callable=AsyncMock
    ) as mock_inference:
        mock_inference.side_effect = Exception("Simulated inference failure")

        with pytest.raises(EvaluationError, match="sample generation") as exc_info:
            await evaluate_metric(job, str(tmp_path))
        assert exc_info.value.index == 0
        assert exc_info.value.phase is EvaluationPhase.SAMPLE_GENERATION
        assert exc_info.value.metric_key == "exact-match"


def _ragas_topic_adherence_job_config(*, ignore_request_failure: bool) -> dict:
    config: dict = {
        "dataset": {
            "rows": [
                {
                    "user_input": "What is the capital of France?",
                    "response": "The capital is Paris.",
                    "reference": "Paris",
                    "retrieved_contexts": ["Paris is the capital and largest city of France."],
                }
            ],
        },
        "metric": {
            "type": "topic_adherence",
            "metric_mode": "f1",
            "judge_model": {
                "name": "test-judge",
                "url": "http://test:8000/v1/chat/completions",
            },
        },
    }
    if ignore_request_failure:
        config["metric"]["ignore_request_failure"] = True
    return config


@pytest.mark.asyncio
async def test_evaluate_metric_ragas_parse_failure_with_ignore_flag_returns_nan_row_error(tmp_path):
    job = MetricJobAdapter.validate_python(_ragas_topic_adherence_job_config(ignore_request_failure=True))

    empty_result = MagicMock()
    empty_result.scores = []
    mock_evaluate = MagicMock(return_value=empty_result)
    with patch("nemo_evaluator_sdk.metrics.ragas.base.get_evaluate_function", return_value=mock_evaluate):
        result = await evaluate_metric(job, str(tmp_path))

    assert len(result.scores) == 1
    assert result.scores[0].name == "topic_adherence"
    assert result.scores[0].nan_count == 1
    assert result.scores[0].count == 0

    with open(tmp_path / EVALUATION_RESULTS_ROW_SCORES_FILE_NAME) as f:
        rows = [json.loads(line) for line in f]
    assert rows[0]["row_index"] == 0
    assert rows[0]["metric_errors"] is None


@pytest.mark.asyncio
async def test_evaluate_metric_ragas_parse_failure_without_ignore_flag_still_returns_nan(tmp_path):
    job = MetricJobAdapter.validate_python(_ragas_topic_adherence_job_config(ignore_request_failure=False))

    empty_result = MagicMock()
    empty_result.scores = []
    mock_evaluate = MagicMock(return_value=empty_result)
    with patch("nemo_evaluator_sdk.metrics.ragas.base.get_evaluate_function", return_value=mock_evaluate):
        result = await evaluate_metric(job, str(tmp_path))

    assert len(result.scores) == 1
    assert result.scores[0].name == "topic_adherence"
    assert result.scores[0].nan_count == 1
    assert result.scores[0].count == 0


@pytest.mark.asyncio
async def test_evaluate_metric_inference_failure_with_empty_message_content_raises_helpful_error(tmp_path):
    job_config = {
        "model": {
            "name": "test-model",
            "url": "http://test:8000/v1/chat/completions",
            "api_key_secret": None,
        },
        "dataset": {
            "rows": [
                {
                    "messages": [{"role": "user", "content": ""}],
                    "expected": "unused",
                }
            ],
        },
        "prompt_template": {"messages": "{{ messages | tojson }}"},
        "metric": {
            "type": "exact-match",
            "name": "test-metric",
            "workspace": "default",
            "reference": "{{item.expected}}",
        },
    }

    job = MetricJobAdapter.validate_python(job_config)

    with patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.make_inference_request", new_callable=AsyncMock
    ) as mock_inference:
        mock_inference.side_effect = Exception("Simulated inference failure")

        with pytest.raises(EvaluationError, match="sample generation") as exc_info:
            await evaluate_metric(job, str(tmp_path))
        assert exc_info.value.index == 0
        assert exc_info.value.phase is EvaluationPhase.SAMPLE_GENERATION
        assert exc_info.value.message == (
            "Row 0 has empty message content and failed inference: Simulated inference failure. "
            "To prevent failure of evaluation, fix the dataset row or set "
            "params.ignore_request_failure=true to skip invalid rows."
        )


@pytest.mark.asyncio
async def test_evaluate_metric_inference_failure_with_empty_prompt_raises_helpful_error(tmp_path):
    job_config = {
        "model": {
            "name": "test-model",
            "url": "http://test:8000/v1/completions",
            "api_key_secret": None,
        },
        "dataset": {
            "rows": [
                {
                    "prompt": "",
                    "expected": "unused",
                }
            ],
        },
        "prompt_template": {"prompt": "{{ prompt }}"},
        "metric": {
            "type": "exact-match",
            "name": "test-metric",
            "workspace": "default",
            "reference": "{{item.expected}}",
        },
    }

    job = MetricJobAdapter.validate_python(job_config)

    with patch(
        "nmp.evaluator.tasks.evaluate_metric.__main__.make_inference_request", new_callable=AsyncMock
    ) as mock_inference:
        mock_inference.side_effect = Exception("Simulated inference failure")

        with pytest.raises(EvaluationError, match="sample generation") as exc_info:
            await evaluate_metric(job, str(tmp_path))
        assert exc_info.value.index == 0
        assert exc_info.value.phase is EvaluationPhase.SAMPLE_GENERATION
        assert exc_info.value.message == (
            "Row 0 has empty prompt and failed inference: Simulated inference failure. "
            "To prevent failure of evaluation, fix the dataset row or set "
            "params.ignore_request_failure=true to skip invalid rows."
        )


class TestEvaluateMetric:
    @pytest.mark.asyncio
    async def test_reraises_keyboard_interrupt_from_scoring_pipeline(self, tmp_path, mocker: MockerFixture):
        job = MetricJobAdapter.validate_python(
            {
                "dataset": {
                    "rows": [{"input": "test input", "expected": "expected output"}],
                },
                "metric": {
                    "type": "exact-match",
                    "name": "test-metric",
                    "workspace": "default",
                    "reference": "{{item.expected}}",
                },
            }
        )
        metric = mocker.Mock()
        metric.type.value = "exact-match"

        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__._load_dataset_items",
            return_value=[{"input": "test input", "expected": "expected output"}],
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.new_metric",
            new_callable=AsyncMock,
            return_value=metric,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.inference_hooks.new_hooks",
            return_value=([], []),
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.run_generated_sample_scoring_pipeline",
            new_callable=AsyncMock,
            side_effect=KeyboardInterrupt,
        )
        get_eval_error = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.get_evaluation_error",
        )

        with pytest.raises(KeyboardInterrupt):
            await evaluate_metric(job, str(tmp_path))

        get_eval_error.assert_not_called()

    @pytest.mark.asyncio
    async def test_normalizes_non_system_exception_from_scoring_pipeline(self, tmp_path, mocker: MockerFixture):
        job = MetricJobAdapter.validate_python(
            {
                "dataset": {
                    "rows": [{"input": "test input", "expected": "expected output"}],
                },
                "metric": {
                    "type": "exact-match",
                    "name": "test-metric",
                    "workspace": "default",
                    "reference": "{{item.expected}}",
                },
            }
        )
        metric = mocker.Mock()
        metric.type.value = "exact-match"
        failure = ValueError("boom")

        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__._load_dataset_items",
            return_value=[{"input": "test input", "expected": "expected output"}],
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.new_metric",
            new_callable=AsyncMock,
            return_value=metric,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.inference_hooks.new_hooks",
            return_value=([], []),
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.run_generated_sample_scoring_pipeline",
            new_callable=AsyncMock,
            side_effect=failure,
        )
        get_eval_error = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.get_evaluation_error",
            return_value=RuntimeError("normalized boom"),
        )

        with pytest.raises(RuntimeError, match="normalized boom"):
            await evaluate_metric(job, str(tmp_path))

        get_eval_error.assert_called_once_with(failure)

    @pytest.mark.asyncio
    async def test_reraises_evaluation_error_from_scoring_pipeline(self, tmp_path, mocker: MockerFixture):
        job = MetricJobAdapter.validate_python(
            {
                "dataset": {
                    "rows": [{"input": "test input", "expected": "expected output"}],
                },
                "metric": {
                    "type": "exact-match",
                    "name": "test-metric",
                    "workspace": "default",
                    "reference": "{{item.expected}}",
                },
            }
        )
        metric = mocker.Mock()
        metric.type.value = "exact-match"
        failure = EvaluationError(
            index=3,
            message="'missing_field' is undefined",
            phase=EvaluationPhase.METRIC_SCORING,
            metric_key="exact-match",
        )

        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__._load_dataset_items",
            return_value=[{"input": "test input", "expected": "expected output"}],
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.new_metric",
            new_callable=AsyncMock,
            return_value=metric,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.inference_hooks.new_hooks",
            return_value=([], []),
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.run_generated_sample_scoring_pipeline",
            new_callable=AsyncMock,
            side_effect=failure,
        )
        log_exception = mocker.patch("nmp.evaluator.tasks.evaluate_metric.__main__.log.exception")

        with pytest.raises(EvaluationError) as exc_info:
            await evaluate_metric(job, str(tmp_path))

        assert exc_info.value is failure
        log_exception.assert_called_once_with(
            "Metric evaluation failed",
            extra={
                "phase": "metric_scoring",
                "metric_key": "exact-match",
                "row_index": 3,
                "error": "'missing_field' is undefined",
            },
        )

    @pytest.mark.asyncio
    async def test_reraises_evaluation_error_from_single_exception_group(self, tmp_path, mocker: MockerFixture):
        from nemo_evaluator_sdk.execution.values import EvaluationError

        job = MetricJobAdapter.validate_python(
            {
                "dataset": {
                    "rows": [{"input": "test input", "expected": "expected output"}],
                },
                "metric": {
                    "type": "exact-match",
                    "name": "test-metric",
                    "workspace": "default",
                    "reference": "{{item.expected}}",
                },
            }
        )
        metric = mocker.Mock()
        metric.type.value = "exact-match"
        failure = EvaluationError(index=4, message="grouped cause")

        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__._load_dataset_items",
            return_value=[{"input": "test input", "expected": "expected output"}],
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.new_metric",
            new_callable=AsyncMock,
            return_value=metric,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.inference_hooks.new_hooks",
            return_value=([], []),
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.run_generated_sample_scoring_pipeline",
            new_callable=AsyncMock,
            side_effect=ExceptionGroup("tasks", [failure]),
        )

        with pytest.raises(EvaluationError) as exc_info:
            await evaluate_metric(job, str(tmp_path))

        assert exc_info.value is failure

    @pytest.mark.asyncio
    async def test_reraises_non_leading_evaluation_error_from_exception_group(self, tmp_path, mocker: MockerFixture):
        from nemo_evaluator_sdk.execution.values import EvaluationError

        job = MetricJobAdapter.validate_python(
            {
                "dataset": {
                    "rows": [{"input": "test input", "expected": "expected output"}],
                },
                "metric": {
                    "type": "exact-match",
                    "name": "test-metric",
                    "workspace": "default",
                    "reference": "{{item.expected}}",
                },
            }
        )
        metric = mocker.Mock()
        metric.type.value = "exact-match"
        failure = EvaluationError(index=5, message="non-leading cause")

        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__._load_dataset_items",
            return_value=[{"input": "test input", "expected": "expected output"}],
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.new_metric",
            new_callable=AsyncMock,
            return_value=metric,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.inference_hooks.new_hooks",
            return_value=([], []),
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.run_generated_sample_scoring_pipeline",
            new_callable=AsyncMock,
            side_effect=ExceptionGroup(
                "tasks",
                [
                    RuntimeError("sibling before"),
                    failure,
                    RuntimeError("sibling after"),
                ],
            ),
        )

        with pytest.raises(EvaluationError) as exc_info:
            await evaluate_metric(job, str(tmp_path))

        assert exc_info.value is failure

    @pytest.mark.asyncio
    async def test_reraises_nested_evaluation_error_from_exception_group(self, tmp_path, mocker: MockerFixture):
        from nemo_evaluator_sdk.execution.values import EvaluationError

        job = MetricJobAdapter.validate_python(
            {
                "dataset": {
                    "rows": [{"input": "test input", "expected": "expected output"}],
                },
                "metric": {
                    "type": "exact-match",
                    "name": "test-metric",
                    "workspace": "default",
                    "reference": "{{item.expected}}",
                },
            }
        )
        metric = mocker.Mock()
        metric.type.value = "exact-match"
        failure = EvaluationError(index=6, message="nested cause")

        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__._load_dataset_items",
            return_value=[{"input": "test input", "expected": "expected output"}],
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.new_metric",
            new_callable=AsyncMock,
            return_value=metric,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.inference_hooks.new_hooks",
            return_value=([], []),
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.run_generated_sample_scoring_pipeline",
            new_callable=AsyncMock,
            side_effect=ExceptionGroup(
                "outer",
                [
                    RuntimeError("sibling"),
                    ExceptionGroup("inner", [RuntimeError("noise"), failure]),
                ],
            ),
        )

        with pytest.raises(EvaluationError) as exc_info:
            await evaluate_metric(job, str(tmp_path))

        assert exc_info.value is failure


@pytest.mark.asyncio
async def test_evaluate_metric_inference_failure_keeps_partial_requests(tmp_path):
    job_config = {
        "model": {
            "name": "test-model",
            "url": "http://test:8000/v1/chat/completions",
            "api_key_secret": None,
        },
        "dataset": {
            "rows": [
                {"input": "test input 1"},
                {"input": "test input 2"},
            ],
        },
        "prompt_template": {"messages": [{"role": "user", "content": "{{input}}"}]},
        "params": {
            "ignore_request_failure": True,
        },
        "metric": {
            "type": "exact-match",
            "name": "test-metric",
            "workspace": "default",
            "reference": "{{item.expected}}",
        },
    }

    job = MetricJobAdapter.validate_python(job_config)

    async def partial_failing_inference(*args, **kwargs):
        request = kwargs.get("request") if "request" in kwargs else args[1]
        inference.requests_log_var.get([]).append({"request": request, "error": "partial failure"})
        raise Exception("Simulated inference failure")

    await evaluate_metric(job, str(tmp_path), inference_fn=partial_failing_inference)

    with open(tmp_path / EVALUATION_RESULTS_ROW_SCORES_FILE_NAME) as f:
        rows = [json.loads(line) for line in f]

    assert len(rows) == 2
    for row in rows:
        assert "row_index" in row
        assert len(row["requests"]) == 1
        assert row["metric_errors"] == {"exact-match": _expected_inference_failure_message(row["row_index"])}
        assert row["requests"][0]["error"] == "partial failure"
        assert row["requests"][0]["request"]["messages"][0]["content"] == row["item"]["input"]


@pytest.mark.asyncio
async def test_evaluate_metric_metric_failure_with_ignore_flag_keeps_nan_row_metric(tmp_path):
    job_config = {
        "model": {
            "name": "test-model",
            "url": "http://test:8000/v1/chat/completions",
            "api_key_secret": None,
        },
        "dataset": {
            "rows": [{"input": "test input"}],
        },
        "prompt_template": {"messages": [{"role": "user", "content": "{{input}}"}]},
        "params": {
            "ignore_request_failure": True,
        },
        "metric": {
            "type": "exact-match",
            "name": "test-metric",
            "workspace": "default",
            "reference": "{{item.expected}}",
        },
    }

    job = MetricJobAdapter.validate_python(job_config)

    async def successful_inference(*args, **kwargs):
        return {"choices": [{"message": {"content": "model answer"}}]}

    result = await evaluate_metric(job, str(tmp_path), inference_fn=successful_inference)

    assert result.scores[0].count == 0
    assert result.scores[0].nan_count == 1

    with open(tmp_path / EVALUATION_RESULTS_ROW_SCORES_FILE_NAME) as f:
        row = json.loads(next(f))

    assert row["row_index"] == 0
    assert row["metrics"]["exact-match"][0]["value"] == "NaN"
    assert "exact-match" in row["metric_errors"]


@pytest.mark.asyncio
async def test_evaluate_metric_online_tool_calling_allows_null_content(tmp_path):
    job_config = {
        "model": {
            "name": "test-model",
            "url": "http://test:8000/v1/chat/completions",
            "api_key_secret": None,
        },
        "dataset": {
            "rows": [
                {
                    "input": "Calculate area",
                    "expected_tool_calls": [
                        {
                            "function": {
                                "name": "calculate_area",
                                "arguments": {"base": 10, "height": 5},
                            }
                        }
                    ],
                }
            ],
        },
        "prompt_template": {"messages": [{"role": "user", "content": "{{input}}"}]},
        "metric": {
            "type": "tool-calling",
            "name": "test-tool-calling",
            "workspace": "default",
            "reference": "{{item.expected_tool_calls}}",
        },
    }

    job = MetricJobAdapter.validate_python(job_config)

    response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "function": {
                                "name": "calculate_area",
                                "arguments": '{"base": 10, "height": 5}',
                            }
                        }
                    ],
                }
            }
        ]
    }

    async def mock_inference(*args, **kwargs):
        return response

    result = await evaluate_metric(job, str(tmp_path), inference_fn=mock_inference)

    scores = {score.name: score for score in result.scores}
    assert scores["function_name_accuracy"].mean == 1.0
    assert scores["function_name_and_args_accuracy"].mean == 1.0


def _make_aggregate_score(name: str, count: int, nan_count: int = 0) -> AggregateRangeScore:
    """Helper to create a minimal AggregateRangeScore for testing."""
    return AggregateRangeScore(
        name=name,
        count=count,
        nan_count=nan_count,
        sum=0.0,
        mean=0.0,
        min=0.0,
        max=0.0,
        std_dev=0.0,
        variance=0.0,
        percentiles=Percentiles(
            p10=0.0,
            p20=0.0,
            p30=0.0,
            p40=0.0,
            p50=0.0,
            p60=0.0,
            p70=0.0,
            p80=0.0,
            p90=0.0,
            p100=0.0,
        ),
        histogram=Histogram(bins=[]),
    )


class TestNoAggregatedMetricScores:
    """Tests for no_aggregated_metric_scores function."""

    def test_empty_scores_returns_true(self):
        """Empty scores list means no valid metrics."""
        result = AggregatedMetricResult(scores=[])
        assert no_aggregated_metric_scores(result) is True

    def test_all_scores_zero_count_returns_true(self):
        """All scores with count=0 (all NaN) means no valid metrics."""
        result = AggregatedMetricResult(
            scores=[
                _make_aggregate_score("score1", count=0, nan_count=5),
                _make_aggregate_score("score2", count=0, nan_count=3),
            ]
        )
        assert no_aggregated_metric_scores(result) is True

    def test_some_valid_scores_returns_false(self):
        """At least one score with count > 0 means we have valid metrics."""
        result = AggregatedMetricResult(
            scores=[
                _make_aggregate_score("score1", count=0, nan_count=5),
                _make_aggregate_score("score2", count=3, nan_count=2),
            ]
        )
        assert no_aggregated_metric_scores(result) is False

    def test_all_valid_scores_returns_false(self):
        """All scores with count > 0 means we have valid metrics."""
        result = AggregatedMetricResult(
            scores=[
                _make_aggregate_score("score1", count=10),
                _make_aggregate_score("score2", count=5),
            ]
        )
        assert no_aggregated_metric_scores(result) is False


class TestJsonDefault:
    """Tests for _json_default function used in JSON serialization."""

    def test_object_with_dict_method(self):
        """Objects with dict() method (LangChain messages, Pydantic v1) are serialized."""

        class MockLangChainMessage:
            def __init__(self, content: str, msg_type: str):
                self.content = content
                self.type = msg_type

            def dict(self):
                return {"content": self.content, "type": self.type}

        msg = MockLangChainMessage("Hello", "human")
        result = _json_default(msg)
        assert result == {"content": "Hello", "type": "human"}

    def test_object_with_model_dump_method(self):
        """Objects with model_dump() method (Pydantic v2) are serialized."""

        class MockPydanticV2Model:
            def __init__(self, value: int):
                self.value = value

            def model_dump(self):
                return {"value": self.value}

        model = MockPydanticV2Model(42)
        result = _json_default(model)
        assert result == {"value": 42}

    def test_object_with_to_dict_method(self):
        """Objects with to_dict() method are serialized."""

        class MockObject:
            def __init__(self, data: str):
                self.data = data

            def to_dict(self):
                return {"data": self.data}

        obj = MockObject("test")
        result = _json_default(obj)
        assert result == {"data": "test"}

    def test_dict_method_takes_precedence(self):
        """dict() method takes precedence over model_dump() and to_dict()."""

        class MockMultiMethod:
            def dict(self):
                return {"method": "dict"}

            def model_dump(self):
                return {"method": "model_dump"}

            def to_dict(self):
                return {"method": "to_dict"}

        obj = MockMultiMethod()
        result = _json_default(obj)
        assert result == {"method": "dict"}

    def test_fallback_to_string(self):
        """Objects without serialization methods fall back to str()."""

        class PlainObject:
            def __str__(self):
                return "PlainObject()"

        obj = PlainObject()
        result = _json_default(obj)
        assert result == "PlainObject()"

    def test_json_dumps_integration(self):
        """Verify _json_default works with json.dumps()."""

        class MockMessage:
            def dict(self):
                return {"content": "test", "type": "human"}

        data = {"messages": [MockMessage()]}
        result = json.dumps(data, default=_json_default)
        parsed = json.loads(result)
        assert parsed == {"messages": [{"content": "test", "type": "human"}]}


def _write_metric_job_config(tmp_path: Path, *, online: bool = False) -> Path:
    config = {
        "dataset": {
            "rows": [{"input": "test input", "expected": "expected output"}],
        },
        "metric": {
            "type": "exact-match",
            "name": "test-metric",
            "workspace": "default",
            "reference": "{{item.expected}}",
        },
    }
    if online:
        config["model"] = {
            "name": "test-model",
            "url": "http://test:8000/v1/chat/completions",
            "api_key_secret": None,
        }
        config["prompt_template"] = {"messages": [{"role": "user", "content": "{{input}}"}]}

    config_path = tmp_path / "job.json"
    config_path.write_text(json.dumps(config))
    return config_path


class TestMetricEvaluationEntrypoint:
    def test_returns_python_module_command(self):
        assert metric_evaluation_entrypoint() == ["python", "-m", "nmp.evaluator.tasks.evaluate_metric"]


class TestMetricEvaluationEntrypointArgs:
    def test_defaults_to_job_runtime_environment(self):
        assert metric_evaluation_entrypoint_args() == []

    def test_includes_progress_tracking_options(self):
        assert metric_evaluation_entrypoint_args(
            progress_tracking_url="https://callback.example.test",
            progress_tracking_interval=25,
        ) == [
            "--progress-tracking-url",
            "https://callback.example.test",
            "--progress-tracking-interval",
            "25",
        ]


class TestLoadDatasetItems:
    def test_apply_optional_fields_defaults_missing_fields(self):
        assert _apply_optional_fields_to_row({"input": "hello"}, ["reference"]) == {
            "input": "hello",
            "reference": "",
        }

    def test_returns_inline_rows(self, mocker: MockerFixture):
        job = mocker.Mock(dataset=DatasetRows(rows=[{"input": "hello"}]), field_mapping=None)
        job.metric = mocker.Mock(optional_fields=[])

        assert _load_dataset_items(job) == [{"input": "hello"}]

    def test_raises_for_empty_inline_rows(self, mocker: MockerFixture):
        job = mocker.Mock(dataset=DatasetRows.model_construct(rows=[]), field_mapping=None)
        job.metric = mocker.Mock(optional_fields=[])

        with pytest.raises(ValueError, match="DatasetRows has no rows"):
            _load_dataset_items(job)

    def test_defaults_optional_fields_for_inline_rows(self, mocker: MockerFixture):
        job = mocker.Mock(dataset=DatasetRows(rows=[{"input": "hello"}]), field_mapping=None)
        job.metric = mocker.Mock(optional_fields=["reference"])

        assert _load_dataset_items(job) == [{"input": "hello", "reference": ""}]

    def test_loads_fileset_rows(self, mocker: MockerFixture):
        job = mocker.Mock(dataset=FilesetRef(root="workspace/fileset"), field_mapping=None)
        job.metric = mocker.Mock(optional_fields=[])
        load_dataset = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.load_dataset_from_ref_as_dicts",
            return_value=[{"input": "from fileset"}],
        )

        assert _load_dataset_items(job, dataset_dir="/tmp/downloads") == [{"input": "from fileset"}]
        load_dataset.assert_called_once_with("workspace/fileset", base_dir="/tmp/downloads")

    def test_loads_fileset_rows_from_runtime_job_storage(
        self, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        job = mocker.Mock(dataset=FilesetRef(root="workspace/fileset"), field_mapping=None)
        job.metric = mocker.Mock(optional_fields=[])
        storage_dir = tmp_path / "job-storage"
        monkeypatch.setenv(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, str(storage_dir))
        load_dataset = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.load_dataset_from_ref_as_dicts",
            return_value=[{"input": "from fileset"}],
        )

        assert _load_dataset_items(job) == [{"input": "from fileset"}]
        load_dataset.assert_called_once_with("workspace/fileset", base_dir=str(storage_dir / "datasets"))

    def test_raises_for_fileset_load_error(self, mocker: MockerFixture):
        job = mocker.Mock(dataset=FilesetRef(root="workspace/fileset"), field_mapping=None)
        job.metric = mocker.Mock(optional_fields=[])
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.load_dataset_from_ref_as_dicts",
            side_effect=DatasetLoadError("bad dataset"),
        )

        with pytest.raises(ValueError, match="Failed to load dataset 'workspace/fileset': bad dataset"):
            _load_dataset_items(job, dataset_dir="/tmp/downloads")

    def test_raises_for_empty_fileset(self, mocker: MockerFixture):
        job = mocker.Mock(dataset=FilesetRef(root="workspace/fileset"), field_mapping=None)
        job.metric = mocker.Mock(optional_fields=[])
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.load_dataset_from_ref_as_dicts",
            return_value=[],
        )

        with pytest.raises(ValueError, match="Dataset 'workspace/fileset' is empty"):
            _load_dataset_items(job, dataset_dir="/tmp/downloads")

    def test_raises_for_unsupported_dataset_type(self, mocker: MockerFixture):
        job = mocker.Mock(dataset="not-supported", field_mapping=None)
        job.metric = mocker.Mock(optional_fields=[])

        with pytest.raises(ValueError, match="Unsupported dataset type: str"):
            _load_dataset_items(job)


class TestEvaluateMetricBranches:
    @pytest.mark.asyncio
    async def test_online_job_configures_progress_tracking_pipeline(self, tmp_path, mocker: MockerFixture):
        job = MetricJobAdapter.validate_python(
            {
                "model": {
                    "name": "test-model",
                    "url": "http://test:8000/v1/chat/completions",
                    "api_key_secret": None,
                    "format": "openai",
                },
                "dataset": {
                    "rows": [
                        {"input": "one", "expected": "ONE"},
                        {"input": "two", "expected": "TWO"},
                        {"input": "three", "expected": "THREE"},
                    ],
                },
                "prompt_template": {"messages": [{"role": "user", "content": "{{input}}"}]},
                "params": {
                    "limit_samples": 2,
                    "ignore_request_failure": True,
                },
                "metric": {
                    "type": "exact-match",
                    "name": "test-metric",
                    "workspace": "default",
                    "reference": "{{item.expected}}",
                },
            }
        )
        progress_tracking = mocker.Mock(interval=5)
        metric = mocker.Mock()
        metric.type.value = "exact-match"
        completed = [
            (
                0,
                None,
                mocker.Mock(item={"input": "one"}, sample={"output_text": "ONE"}),
            ),
            (
                1,
                None,
                mocker.Mock(item={"input": "two"}, sample={"output_text": "TWO"}),
            ),
        ]
        finalized = mocker.Mock(
            aggregate_scores=AggregatedMetricResult(scores=[_make_aggregate_score("exact-match", count=2)]),
            row_scores=[],
        )

        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__._load_dataset_items",
            return_value=[
                {"input": "one", "expected": "ONE"},
                {"input": "two", "expected": "TWO"},
                {"input": "three", "expected": "THREE"},
            ],
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.new_metric",
            new_callable=AsyncMock,
            return_value=metric,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.get_platform_headers",
            return_value={"x-platform": "evaluator"},
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.inference_hooks.new_hooks",
            return_value=(["pre-hook"], ["post-hook"]),
        )
        run_pipeline = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.run_generated_sample_scoring_pipeline",
            new_callable=AsyncMock,
            return_value=completed,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.finalize_evaluation_result",
            new_callable=AsyncMock,
            return_value=finalized,
        )
        mocker.patch("nmp.evaluator.tasks.evaluate_metric.__main__.job_artifacts_dump")

        result = await evaluate_metric(job, str(tmp_path), progress_tracking=progress_tracking)

        assert result == finalized.aggregate_scores
        assert progress_tracking.total_samples == 2
        assert run_pipeline.await_args is not None
        pipeline = run_pipeline.await_args.args[0]
        assert pipeline.rows == [
            {"input": "one", "expected": "ONE"},
            {"input": "two", "expected": "TWO"},
        ]
        assert pipeline.target == job.model
        assert pipeline.prompt_template == job.prompt_template
        assert pipeline.default_headers == {"x-platform": "evaluator"}
        assert pipeline.params is job.params
        assert pipeline.params.ignore_request_failure is True
        assert pipeline.preprocess_hooks == ["pre-hook"]
        assert pipeline.postprocess_hooks[0] == "post-hook"
        assert isinstance(pipeline.postprocess_hooks[1], ProgressTrackingHook)
        assert pipeline.postprocess_hooks[1].progress_tracking is progress_tracking

    @pytest.mark.asyncio
    async def test_evaluate_metric_attaches_platform_headers_to_agent_pipeline(self, tmp_path, mocker: MockerFixture):
        job = MetricJobAdapter.validate_python(
            {
                "dataset": {"rows": [{"input": "one", "expected": "ONE"}]},
                "metric": {
                    "type": "exact-match",
                    "name": "test-metric",
                    "workspace": "default",
                    "reference": "{{item.expected}}",
                },
                "agent": {
                    "url": "http://nemo-platform-api.default.svc.cluster.local/v1/agents/test-agent",
                    "name": "test-agent",
                    "format": "generic",
                    "body": {"messages": "{{messages}}"},
                    "response_path": "$.answer",
                },
                "prompt_template": {"messages": [{"role": "user", "content": "{{item.input}}"}]},
                "params": {"parallelism": 1, "ignore_request_failure": False},
            }
        )
        metric = mocker.Mock()
        metric.type.value = "exact-match"
        finalized = mocker.Mock(
            aggregate_scores=AggregatedMetricResult(scores=[_make_aggregate_score("exact-match", count=1)]),
            row_scores=[],
        )
        get_platform_headers = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.get_platform_headers",
            return_value={"x-platform": "evaluator"},
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.new_metric",
            new_callable=AsyncMock,
            return_value=metric,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.inference_hooks.new_hooks",
            return_value=([], []),
        )
        run_pipeline = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.run_generated_sample_scoring_pipeline",
            new_callable=AsyncMock,
            return_value=[],
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.finalize_evaluation_result",
            new_callable=AsyncMock,
            return_value=finalized,
        )
        mocker.patch("nmp.evaluator.tasks.evaluate_metric.__main__.job_artifacts_dump")

        await evaluate_metric(job, str(tmp_path))

        get_platform_headers.assert_called_once_with(job.agent.url)
        assert run_pipeline.await_args is not None
        pipeline = run_pipeline.await_args.args[0]
        assert pipeline.target == job.agent
        assert pipeline.default_headers == {"x-platform": "evaluator"}
        assert pipeline.params is job.params
        assert pipeline.params.ignore_request_failure is False


class TestMain:
    @pytest.mark.asyncio
    async def test_defaults_to_job_runtime_environment(self, tmp_path, mocker: MockerFixture, monkeypatch):
        config_file = _write_metric_job_config(tmp_path)
        storage_dir = tmp_path / "job-storage"
        expected_results_dir = str(storage_dir / "results")
        evaluation_result = AggregatedMetricResult(scores=[_make_aggregate_score("exact-match", count=1)])

        monkeypatch.setenv(NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, str(config_file))
        monkeypatch.setenv(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, str(storage_dir))

        evaluate = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.evaluate_metric",
            new_callable=AsyncMock,
            return_value=evaluation_result,
        )

        assert await main(["--skip-upload-results", "true"]) == 0
        evaluate.assert_awaited_once_with(mocker.ANY, expected_results_dir, None)

    @pytest.mark.asyncio
    async def test_uploads_results_and_updates_progress(
        self, tmp_path, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
    ):
        config_file = _write_metric_job_config(tmp_path)
        results_dir = tmp_path / "results"
        results_config = mocker.Mock(NEMO_JOB_ID="job-123", NEMO_JOB_WORKSPACE="workspace")
        progress_tracking = mocker.Mock()
        evaluation_result = AggregatedMetricResult(scores=[_make_aggregate_score("exact-match", count=1)])
        sdk = mocker.Mock()
        monkeypatch.setenv(NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, str(config_file))
        monkeypatch.setenv(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, str(tmp_path))

        results_handler_cls = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.ResultsHandlerConfig",
            return_value=results_config,
        )
        progress_tracking_cls = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.ProgressTracking",
            return_value=progress_tracking,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.evaluate_metric",
            new_callable=AsyncMock,
            return_value=evaluation_result,
        )
        handle_results = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.handle_results_async",
            new_callable=AsyncMock,
        )
        get_sdk = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.get_async_platform_sdk",
            return_value=sdk,
        )

        exit_code = await main(
            [
                "--progress-tracking-url",
                "https://callback.example.test",
                "--progress-tracking-interval",
                "25",
                "--progress-tracking-interval-seconds",
                "30",
            ]
        )

        assert exit_code == 0
        results_handler_cls.assert_called_once_with()
        progress_tracking_cls.assert_called_once_with("https://callback.example.test", "25", "30")
        get_sdk.assert_called_once_with(as_service="evaluator", internal=True)
        handle_results.assert_awaited_once_with(
            mocker.ANY,
            results_config,
            str(results_dir),
            sdk=sdk,
        )
        progress_tracking.update_progress.assert_called_once_with(100)
        progress_tracking.stop.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_raises_when_no_aggregated_scores_exist(
        self, tmp_path, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
    ):
        config_file = _write_metric_job_config(tmp_path)
        results_config = mocker.Mock(NEMO_JOB_ID="job-123", NEMO_JOB_WORKSPACE="workspace")
        monkeypatch.setenv(NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, str(config_file))
        monkeypatch.setenv(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, str(tmp_path))

        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.ResultsHandlerConfig",
            return_value=results_config,
        )
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.evaluate_metric",
            new_callable=AsyncMock,
            return_value=AggregatedMetricResult(scores=[]),
        )
        handle_results = mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.handle_results_async",
            new_callable=AsyncMock,
        )

        with pytest.raises(ValueError, match="no evaluation results detected"):
            await main([])

        handle_results.assert_awaited_once()


class TestRun:
    def test_returns_async_main_result(self, mocker: MockerFixture):
        register_handlers = mocker.patch("nmp.evaluator.tasks.evaluate_metric.__main__.register_task_signal_handlers")
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.asyncio.run",
            side_effect=lambda coro: (coro.close(), 7)[1],
        )

        assert run([]) == 7
        register_handlers.assert_called_once_with()

    def test_returns_zero_on_keyboard_interrupt(self, mocker: MockerFixture):
        mocker.patch("nmp.evaluator.tasks.evaluate_metric.__main__.register_task_signal_handlers")
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.asyncio.run",
            side_effect=lambda coro: (coro.close(), (_ for _ in ()).throw(KeyboardInterrupt()))[1],
        )
        log_info = mocker.patch("nmp.evaluator.tasks.evaluate_metric.__main__.log.info")

        assert run() == 0
        log_info.assert_called_once()

    def test_returns_one_on_exception(self, mocker: MockerFixture):
        mocker.patch("nmp.evaluator.tasks.evaluate_metric.__main__.register_task_signal_handlers")
        mocker.patch(
            "nmp.evaluator.tasks.evaluate_metric.__main__.asyncio.run",
            side_effect=lambda coro: (coro.close(), (_ for _ in ()).throw(RuntimeError("boom")))[1],
        )
        log_exception = mocker.patch("nmp.evaluator.tasks.evaluate_metric.__main__.log.exception")

        assert run() == 1
        log_exception.assert_called_once_with("Error in evaluate_metric task")
