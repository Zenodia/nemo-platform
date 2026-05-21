# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for metric_results module."""

import json
from unittest.mock import patch

import pytest
from nemo_evaluator_sdk.values import MetricScore, ScoreStats
from nmp.evaluator.app.jobs.constants import normalize_eval_harness
from nmp.evaluator.app.jobs.metric_results import _get_results_parser
from nmp.evaluator.app.jobs.result_parsers.custom import CustomResultsParser
from nmp.evaluator.app.jobs.result_parsers.evalfactory import (
    EvalFactoryResultsParser,
    _normalize_cached_outputs_row,
    _parse_evalfactory_bfcl_rows,
    _parse_evalfactory_cached_outputs_rows,
    _parse_evalfactory_csv_rows,
    _parse_evalfactory_predictions_rows,
    _parse_evalfactory_retriever_rows,
    _parse_evalfactory_scores,
    _scores_to_aggregated_result,
    _select_evalfactory_row_source,
    resolve_evalfactory_results_file_path,
)
from nmp.evaluator.app.values import (
    DeprecatedMetricResult,
    DeprecatedScoreValue,
    EvaluationResult,
    GroupResult,
    TaskResult,
)


class TestParseEvalFactoryResults:
    """Tests for _parse_evalfactory_scores function."""

    def test_parses_tasks_only(self):
        """Test parsing results that only have tasks (e.g., simple_evals, lm-eval-harness)."""
        mock_result = EvaluationResult(
            job="test-job",
            tasks={
                "task1": TaskResult(
                    metrics={"metric1": DeprecatedMetricResult(scores={"accuracy": DeprecatedScoreValue(value=0.85)})}
                )
            },
            groups=None,
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            scores = _parse_evalfactory_scores("test-job", "/fake/path")

        assert len(scores) == 1
        assert scores[0].name == "accuracy"
        assert scores[0].value == 0.85

    def test_parses_groups_only(self):
        """Test parsing results that only have groups (e.g., BFCL)."""
        mock_result = EvaluationResult(
            job="test-job",
            tasks=None,
            groups={
                "group1": GroupResult(
                    metrics={"metric1": DeprecatedMetricResult(scores={"f1": DeprecatedScoreValue(value=0.75)})}
                )
            },
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            scores = _parse_evalfactory_scores("test-job", "/fake/path")

        assert len(scores) == 1
        assert scores[0].name == "f1"
        assert scores[0].value == 0.75

    def test_no_duplicate_scores_when_tasks_and_groups_have_same_data(self):
        """Test that scores are NOT duplicated when both tasks and groups contain the same data.

        This regression test verifies fix for bug 5872277: some EvalFactory containers
        output identical scores in both tasks and groups sections of results.yml,
        causing duplicate scores in aggregate_scores API.
        """
        # Create identical scores in both tasks and groups
        shared_scores = {"accuracy": DeprecatedScoreValue(value=0.90)}

        mock_result = EvaluationResult(
            job="test-job",
            tasks={"task1": TaskResult(metrics={"metric1": DeprecatedMetricResult(scores=shared_scores.copy())})},
            groups={"group1": GroupResult(metrics={"metric1": DeprecatedMetricResult(scores=shared_scores.copy())})},
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            scores = _parse_evalfactory_scores("test-job", "/fake/path")

        # Should only have 1 score, not 2 (tasks takes priority)
        assert len(scores) == 1
        assert scores[0].name == "accuracy"
        assert scores[0].value == 0.90

    def test_tasks_take_priority_over_groups_for_same_score_name(self):
        """Test that tasks scores take priority when same score name exists in both."""
        mock_result = EvaluationResult(
            job="test-job",
            tasks={
                "task1": TaskResult(
                    metrics={
                        "metric1": DeprecatedMetricResult(scores={"shared_score": DeprecatedScoreValue(value=0.80)})
                    }
                )
            },
            groups={
                "group1": GroupResult(
                    metrics={
                        "metric1": DeprecatedMetricResult(scores={"shared_score": DeprecatedScoreValue(value=0.70)})
                    }
                )
            },
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            scores = _parse_evalfactory_scores("test-job", "/fake/path")

        # Should only have task score value (0.80), not group score value (0.70)
        assert len(scores) == 1
        assert scores[0].name == "shared_score"
        assert scores[0].value == 0.80

    def test_merges_different_scores_from_tasks_and_groups(self):
        """Test that different scores from tasks and groups are both included.

        This is important for harnesses that output different metrics in tasks vs groups.
        """
        mock_result = EvaluationResult(
            job="test-job",
            tasks={
                "task1": TaskResult(
                    metrics={
                        "metric1": DeprecatedMetricResult(scores={"task_only_score": DeprecatedScoreValue(value=0.80)})
                    }
                )
            },
            groups={
                "group1": GroupResult(
                    metrics={
                        "metric1": DeprecatedMetricResult(scores={"group_only_score": DeprecatedScoreValue(value=0.70)})
                    }
                )
            },
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            scores = _parse_evalfactory_scores("test-job", "/fake/path")

        # Should have BOTH scores since they have different names
        assert len(scores) == 2
        score_names = {s.name for s in scores}
        assert score_names == {"task_only_score", "group_only_score"}

    def test_multiple_tasks_with_multiple_metrics(self):
        """Test parsing multiple tasks with multiple metrics and scores."""
        mock_result = EvaluationResult(
            job="test-job",
            tasks={
                "task1": TaskResult(
                    metrics={
                        "metric1": DeprecatedMetricResult(
                            scores={
                                "accuracy": DeprecatedScoreValue(value=0.85),
                                "precision": DeprecatedScoreValue(value=0.80),
                            }
                        ),
                        "metric2": DeprecatedMetricResult(scores={"recall": DeprecatedScoreValue(value=0.75)}),
                    }
                ),
                "task2": TaskResult(
                    metrics={"metric3": DeprecatedMetricResult(scores={"f1": DeprecatedScoreValue(value=0.78)})}
                ),
            },
            groups=None,
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            scores = _parse_evalfactory_scores("test-job", "/fake/path")

        assert len(scores) == 4
        score_names = {s.name for s in scores}
        assert score_names == {"accuracy", "precision", "recall", "f1"}

    def test_raises_on_no_valid_scores(self):
        """Test that ValueError is raised when no valid scores are found."""
        mock_result = EvaluationResult(
            job="test-job",
            tasks={},
            groups={},
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            with pytest.raises(ValueError, match="no evaluation results detected"):
                _parse_evalfactory_scores("test-job", "/fake/path")

    def test_empty_tasks_falls_back_to_groups(self):
        """Test that empty tasks dict falls back to groups."""
        mock_result = EvaluationResult(
            job="test-job",
            tasks={},  # Empty but truthy
            groups={
                "group1": GroupResult(
                    metrics={
                        "metric1": DeprecatedMetricResult(scores={"group_score": DeprecatedScoreValue(value=0.65)})
                    }
                )
            },
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            scores = _parse_evalfactory_scores("test-job", "/fake/path")

        # Empty dict is falsy, so groups should be used
        assert len(scores) == 1
        assert scores[0].name == "group_score"

    def test_same_score_name_across_tasks_last_wins(self):
        """Test behavior when multiple tasks have the same score name.

        When multiple tasks have the same score name with different values,
        the last task's value is kept. This is documented behavior - if distinct
        values are needed, tasks should use unique score names.
        """
        mock_result = EvaluationResult(
            job="test-job",
            tasks={
                "task1": TaskResult(
                    metrics={"metric1": DeprecatedMetricResult(scores={"accuracy": DeprecatedScoreValue(value=0.85)})}
                ),
                "task2": TaskResult(
                    metrics={"metric1": DeprecatedMetricResult(scores={"accuracy": DeprecatedScoreValue(value=0.90)})}
                ),
            },
            groups=None,
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            scores = _parse_evalfactory_scores("test-job", "/fake/path")

        # Only one accuracy score should be present (last task wins due to dict iteration)
        assert len(scores) == 1
        assert scores[0].name == "accuracy"
        # Note: The value depends on dict iteration order (Python 3.7+ preserves insertion order)
        # In practice, EvalFactory containers use unique score names per task

    def test_preserves_score_stats(self):
        """Test that score stats are preserved when parsing."""
        mock_result = EvaluationResult(
            job="test-job",
            tasks={
                "task1": TaskResult(
                    metrics={
                        "metric1": DeprecatedMetricResult(
                            scores={
                                "accuracy": DeprecatedScoreValue(
                                    value=0.85, stats=ScoreStats(count=100, mean=0.85, min=0.5, max=1.0)
                                )
                            }
                        )
                    }
                )
            },
            groups=None,
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            scores = _parse_evalfactory_scores("test-job", "/fake/path")

        assert len(scores) == 1
        assert scores[0].stats is not None
        assert scores[0].stats.count == 100
        assert scores[0].stats.mean == 0.85

    def test_accepts_nan_only_scores_when_scores_exist(self):
        """Regression: system metrics can emit NaN scores without groups."""
        mock_result = EvaluationResult(
            job="test-job",
            tasks={
                "rag": TaskResult(
                    metrics={
                        "rag_response_relevancy": DeprecatedMetricResult(
                            scores={"response_relevancy": DeprecatedScoreValue(value=float("nan"))}
                        )
                    }
                )
            },
            groups=None,
        )

        with patch(
            "nmp.evaluator.app.jobs.result_parsers.evalfactory.load_evaluation_result", return_value=mock_result
        ):
            scores = _parse_evalfactory_scores("test-job", "/fake/path")

        assert len(scores) == 1
        assert scores[0].name == "response_relevancy"
        assert scores[0].value != scores[0].value  # NaN


class TestMetricResultConversion:
    def test_converts_metric_result_to_aggregated_schema(self):
        scores = [
            MetricScore(
                name="accuracy",
                value=0.85,
                stats=ScoreStats(count=10, sum=8.5, mean=0.85, min=0.1, max=1.0, variance=0.04, stddev=0.2),
            )
        ]

        aggregated = _scores_to_aggregated_result(scores)
        assert len(aggregated.scores) == 1
        score = aggregated.scores[0]
        assert score.name == "accuracy"
        assert score.count == 10
        assert score.mean == 0.85
        assert score.score_type == "range"

    def test_nan_only_score_uses_null_for_undefined_aggregate_stats(self):
        scores = [MetricScore(name="response_relevancy", value=float("nan"))]

        aggregated = _scores_to_aggregated_result(scores)
        assert len(aggregated.scores) == 1
        score = aggregated.scores[0]
        assert score.name == "response_relevancy"
        assert score.count == 0
        assert score.nan_count == 1
        assert score.mean is None
        assert score.min is None
        assert score.max is None
        assert score.std_dev is None
        assert score.variance is None
        assert score.sum is None
        assert score.percentiles is None

    def test_nan_only_score_with_zero_placeholder_stats_converts_to_null_aggregates(self):
        scores = [
            MetricScore(
                name="response_relevancy",
                value=float("nan"),
                stats=ScoreStats(count=0, nan_count=1, mean=0.0, min=0.0, max=0.0, sum=0.0, variance=0.0, stddev=0.0),
            )
        ]

        aggregated = _scores_to_aggregated_result(scores)
        score = aggregated.scores[0]
        assert score.count == 0
        assert score.nan_count == 1
        assert score.mean is None
        assert score.min is None
        assert score.max is None
        assert score.sum is None
        assert score.variance is None
        assert score.std_dev is None
        assert score.percentiles is None


class TestPrepareEvalFactoryResults:
    def test_creates_empty_row_scores_when_missing(self, tmp_path):
        results_file = tmp_path / "results.yml"
        results_file.write_text("tasks: {}")

        parsed = [MetricScore(name="accuracy", value=1.0)]
        with patch("nmp.evaluator.app.jobs.result_parsers.evalfactory._parse_evalfactory_scores", return_value=parsed):
            prepared = EvalFactoryResultsParser(job_id="job-1", eval_harness="retriever").prepare_results(str(tmp_path))

        assert prepared.aggregate_scores_path.endswith("aggregate-scores.json")
        assert prepared.row_scores_path is not None
        assert prepared.row_scores_path.endswith("row-scores.jsonl")
        assert (tmp_path / "row-scores.jsonl").exists()
        assert (tmp_path / "row-scores.jsonl").read_text() == ""
        aggregate = json.loads((tmp_path / "aggregate-scores.json").read_text())
        assert "scores" in aggregate

    def test_parses_retriever_cached_outputs_to_row_scores(self, tmp_path):
        results_file = tmp_path / "results.yml"
        results_file.write_text("tasks: {}")
        retriever_rows = tmp_path / "results" / "retriever_cached_outputs.json"
        retriever_rows.parent.mkdir(parents=True, exist_ok=True)
        retriever_rows.write_text(
            json.dumps(
                {
                    "q1": {"retrieved_docs": [{"doc_id": "d1", "score": 0.1}]},
                    "q2": {"retrieved_docs": [{"doc_id": "d2", "score": 0.2}]},
                }
            )
        )

        parsed = [MetricScore(name="accuracy", value=1.0)]
        with patch("nmp.evaluator.app.jobs.result_parsers.evalfactory._parse_evalfactory_scores", return_value=parsed):
            prepared = EvalFactoryResultsParser(job_id="job-1", eval_harness="retriever").prepare_results(str(tmp_path))

        assert prepared.row_scores_path is not None
        row_lines = (tmp_path / "row-scores.jsonl").read_text().splitlines()
        assert len(row_lines) == 2
        first = json.loads(row_lines[0])
        second = json.loads(row_lines[1])
        assert first["item"] == {"query_id": "q1"}
        assert second["item"] == {"query_id": "q2"}
        assert first["row_index"] is None
        assert second["row_index"] is None
        assert first["metrics"] == {}
        assert second["metrics"] == {}
        assert first["metric_errors"] is None
        assert second["metric_errors"] is None
        assert "error" not in first
        assert "error" not in second
        assert "retriever" in first
        assert "retriever" in second

    def test_overwrites_existing_empty_row_scores(self, tmp_path):
        results_file = tmp_path / "results.yml"
        results_file.write_text("tasks: {}")
        (tmp_path / "row-scores.jsonl").write_text("")
        predictions = tmp_path / "artifacts" / "predictions.json"
        predictions.parent.mkdir(parents=True, exist_ok=True)
        predictions.write_text(json.dumps(["p1", "p2"]))

        parsed = [MetricScore(name="accuracy", value=1.0)]
        with patch("nmp.evaluator.app.jobs.result_parsers.evalfactory._parse_evalfactory_scores", return_value=parsed):
            EvalFactoryResultsParser(job_id="job-1", eval_harness="bigcode_eval_harness").prepare_results(str(tmp_path))

        row_lines = (tmp_path / "row-scores.jsonl").read_text().splitlines()
        assert len(row_lines) == 2

    def test_loads_results_yml_from_artifacts_directory(self, tmp_path):
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        results_file = artifacts_dir / "results.yml"
        results_file.write_text("tasks: {}")

        parsed = [MetricScore(name="accuracy", value=1.0)]
        with patch("nmp.evaluator.app.jobs.result_parsers.evalfactory._parse_evalfactory_scores", return_value=parsed):
            prepared = EvalFactoryResultsParser(job_id="job-1", eval_harness="retriever").prepare_results(str(tmp_path))

        assert prepared.aggregate_scores_path.endswith("aggregate-scores.json")
        assert (tmp_path / "aggregate-scores.json").exists()


class TestEvalFactoryResultsPathResolution:
    def test_resolves_results_yml_from_artifacts_directory(self, tmp_path):
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        results_path = artifacts_dir / "results.yml"
        results_path.write_text("tasks: {}")

        resolved = resolve_evalfactory_results_file_path(str(tmp_path))
        assert resolved is not None
        assert resolved.endswith("artifacts/results.yml")


class TestEvalFactoryRetrieverRowsParsing:
    def test_raises_when_retriever_artifact_is_not_object(self, tmp_path):
        artifact_path = tmp_path / "retriever_cached_outputs.json"
        artifact_path.write_text(json.dumps([{"query_id": "q1"}]))

        with pytest.raises(ValueError, match="Expected EvalFactory retriever row artifact to be a JSON object"):
            _parse_evalfactory_retriever_rows(str(artifact_path))

    def test_raises_when_retriever_entry_is_not_object(self, tmp_path):
        artifact_path = tmp_path / "retriever_cached_outputs.json"
        artifact_path.write_text(json.dumps({"q1": "invalid"}))

        with pytest.raises(ValueError, match="Invalid EvalFactory retriever row artifact entry type"):
            _parse_evalfactory_retriever_rows(str(artifact_path))


class TestEvalFactoryCachedOutputsRowsParsing:
    def test_prefers_known_cached_outputs_filename_over_other_jsonl(self, tmp_path):
        (tmp_path / "artifacts").mkdir()
        (tmp_path / "artifacts" / "misc.jsonl").write_text(json.dumps({"ignored": True}) + "\n")
        (tmp_path / "artifacts" / "answer_acc.jsonl").write_text(json.dumps({"question": "q1"}) + "\n")

        source = _select_evalfactory_row_source(str(tmp_path), "simple_evals")
        assert source is not None
        assert source[0] == "cached-outputs"
        assert source[1].endswith("answer_acc.jsonl")

    def test_ignores_unknown_jsonl_filename(self, tmp_path):
        artifact_path = tmp_path / "unknown_rows.jsonl"
        artifact_path.write_text(json.dumps({"question": "q1"}) + "\n")

        results_file = tmp_path / "results.yml"
        results_file.write_text("tasks: {}")
        parsed = [MetricScore(name="accuracy", value=1.0)]
        with patch("nmp.evaluator.app.jobs.result_parsers.evalfactory._parse_evalfactory_scores", return_value=parsed):
            prepared = EvalFactoryResultsParser(job_id="job-1", eval_harness="simple_evals").prepare_results(
                str(tmp_path)
            )

        assert prepared.row_scores_path is not None
        row_lines = (tmp_path / "row-scores.jsonl").read_text().splitlines()
        assert len(row_lines) == 0

    def test_ignores_generic_scores_jsonl_filename(self, tmp_path):
        artifact_path = tmp_path / "scores.jsonl"
        artifact_path.write_text(json.dumps({"question": "q1", "score": 1.0}) + "\n")

        results_file = tmp_path / "results.yml"
        results_file.write_text("tasks: {}")
        parsed = [MetricScore(name="accuracy", value=1.0)]
        with patch("nmp.evaluator.app.jobs.result_parsers.evalfactory._parse_evalfactory_scores", return_value=parsed):
            prepared = EvalFactoryResultsParser(job_id="job-1", eval_harness="simple_evals").prepare_results(
                str(tmp_path)
            )

        assert prepared.row_scores_path is not None
        row_lines = (tmp_path / "row-scores.jsonl").read_text().splitlines()
        assert len(row_lines) == 0

    def test_parses_nested_samples_jsonl_filename(self, tmp_path):
        samples_dir = tmp_path / "artifacts" / "mock-model"
        samples_dir.mkdir(parents=True)
        artifact_path = samples_dir / "samples_gsm8k_run.jsonl"
        artifact_path.write_text(json.dumps({"doc_id": 0, "doc": {"question": "q1"}}) + "\n")

        results_file = tmp_path / "results.yml"
        results_file.write_text("tasks: {}")
        parsed = [MetricScore(name="accuracy", value=1.0)]
        with patch("nmp.evaluator.app.jobs.result_parsers.evalfactory._parse_evalfactory_scores", return_value=parsed):
            prepared = EvalFactoryResultsParser(job_id="job-1", eval_harness="lm_eval_harness").prepare_results(
                str(tmp_path)
            )

        assert prepared.row_scores_path is not None
        row_lines = (tmp_path / "row-scores.jsonl").read_text().splitlines()
        assert len(row_lines) == 1
        parsed_row = json.loads(row_lines[0])
        assert parsed_row["item"]["doc_id"] == 0
        assert parsed_row["item"]["doc"]["question"] == "q1"
        assert parsed_row["metrics"] == {}
        assert parsed_row["requests"] == []

    def test_parses_cached_outputs_jsonl_rows(self, tmp_path):
        artifact_path = tmp_path / "answer_acc.jsonl"
        artifact_path.write_text(
            "\n".join(
                [
                    json.dumps({"question": "q1", "answer": "a1"}),
                    json.dumps({"item": {"question": "q2"}, "sample": {"output_text": "a2"}}),
                ]
            )
        )

        rows = _parse_evalfactory_cached_outputs_rows(str(artifact_path))
        assert len(rows) == 2
        assert rows[0]["item"]["question"] == "q1"
        assert rows[0]["sample"] == {}
        assert rows[0]["metrics"] == {}
        assert rows[0]["requests"] == []
        assert rows[1]["item"]["question"] == "q2"
        assert rows[1]["sample"]["output_text"] == "a2"
        assert rows[1]["metrics"] == {}
        assert rows[1]["requests"] == []

    def test_raises_on_non_object_cached_outputs_row(self, tmp_path):
        artifact_path = tmp_path / "answer_acc.jsonl"
        artifact_path.write_text(json.dumps(["not-an-object"]))

        with pytest.raises(ValueError, match="Invalid EvalFactory cached-outputs row"):
            _parse_evalfactory_cached_outputs_rows(str(artifact_path))

    def test_normalize_cached_row_preserves_existing_item_sample(self):
        normalized = _normalize_cached_outputs_row({"item": {"x": 1}, "sample": {"y": 2}})
        assert normalized["item"] == {"x": 1}
        assert normalized["sample"] == {"y": 2}
        assert normalized["metrics"] == {}
        assert normalized["requests"] == []


class TestEvalFactoryBenchmarkRowsParsing:
    def test_parses_aegis_output_csv(self, tmp_path):
        artifact_path = tmp_path / "output.csv"
        artifact_path.write_text("prompt,response,safe\np1,r1,true\np2,r2,false\n")

        rows = _parse_evalfactory_csv_rows(str(artifact_path))
        assert len(rows) == 2
        assert rows[0]["item"]["row_index"] == 0
        assert rows[0]["benchmark"]["prompt"] == "p1"
        assert rows[1]["benchmark"]["safe"] == "false"

    def test_parses_humaneval_predictions_json(self, tmp_path):
        artifact_path = tmp_path / "predictions.json"
        artifact_path.write_text(json.dumps(["def foo(): pass", "def bar(): pass"]))

        rows = _parse_evalfactory_predictions_rows(str(artifact_path))
        assert len(rows) == 2
        assert rows[0]["item"]["row_index"] == 0
        assert rows[1]["prediction"] == "def bar(): pass"

    def test_parses_bfcl_ndjson_payload(self, tmp_path):
        artifact_path = tmp_path / "BFCL_v3_simple_result.json"
        artifact_path.write_text(
            "\n".join(
                [
                    json.dumps({"id": "simple_0", "result": "{}"}),
                    json.dumps({"id": "simple_1", "result": "{}"}),
                ]
            )
        )

        rows = _parse_evalfactory_bfcl_rows(str(artifact_path))
        assert len(rows) == 2
        assert rows[0]["item"]["id"] == "simple_0"
        assert rows[1]["item"]["id"] == "simple_1"


class TestEvalFactoryHarnessRouting:
    def test_selects_retriever_rows_from_harness(self, tmp_path):
        retriever_rows = tmp_path / "results" / "retriever_cached_outputs.json"
        retriever_rows.parent.mkdir(parents=True, exist_ok=True)
        retriever_rows.write_text(json.dumps({"q1": {"retrieved_docs": []}}))

        source = _select_evalfactory_row_source(str(tmp_path), "retriever")
        assert source is not None
        assert source[0] == "retriever"
        assert source[1].endswith("retriever_cached_outputs.json")

    def test_selects_bfcl_rows_from_harness(self, tmp_path):
        bfcl_rows = tmp_path / "results" / "result" / "bfcl" / "simple.json"
        bfcl_rows.parent.mkdir(parents=True, exist_ok=True)
        bfcl_rows.write_text(json.dumps({"id": "simple_0"}) + "\n")

        source = _select_evalfactory_row_source(str(tmp_path), "bfcl")
        assert source is not None
        assert source[0] == "benchmark"
        assert source[2] == "bfcl-ndjson"

    def test_selects_agentic_rows_from_harness(self, tmp_path):
        agentic_rows = tmp_path / "results" / "trajectory_eval_input.jsonl"
        agentic_rows.parent.mkdir(parents=True, exist_ok=True)
        agentic_rows.write_text(json.dumps({"question": "q1"}) + "\n")

        source = _select_evalfactory_row_source(str(tmp_path), "agentic_eval")
        assert source is not None
        assert source[0] == "cached-outputs"
        assert source[1].endswith("trajectory_eval_input.jsonl")


class TestResultsParserSelection:
    def test_uses_custom_parser_for_evaluator_harness(self, tmp_path):
        parser = _get_results_parser("job-1", str(tmp_path), eval_harness="evaluator")
        assert isinstance(parser, CustomResultsParser)

    def test_uses_evalfactory_parser_for_non_evaluator_harness(self, tmp_path):
        parser = _get_results_parser("job-1", str(tmp_path), eval_harness="retriever")
        assert isinstance(parser, EvalFactoryResultsParser)

    def test_defaults_to_custom_parser_when_harness_not_set(self, tmp_path):
        parser = _get_results_parser("job-1", str(tmp_path))
        assert isinstance(parser, CustomResultsParser)

    def test_blank_harness_defaults_to_custom_parser(self, tmp_path):
        parser = _get_results_parser("job-1", str(tmp_path), eval_harness="   ")
        assert isinstance(parser, CustomResultsParser)

    def test_raises_for_unknown_harness(self, tmp_path):
        with pytest.raises(ValueError, match="Unsupported eval harness"):
            _get_results_parser("job-1", str(tmp_path), eval_harness="not-a-harness")


class TestEvalHarnessNormalization:
    def test_normalize_valid_eval_harness(self):
        assert normalize_eval_harness("retriever") == "retriever"

    def test_normalize_none_defaults_to_evaluator(self):
        assert normalize_eval_harness(None) == "evaluator"

    def test_normalize_blank_defaults_to_evaluator(self):
        assert normalize_eval_harness("   ") == "evaluator"

    def test_normalize_invalid_raises(self):
        with pytest.raises(ValueError, match="Unsupported eval harness"):
            normalize_eval_harness("bad-harness")
