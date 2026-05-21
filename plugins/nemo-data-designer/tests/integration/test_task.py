# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import io
import logging
import tarfile
import tempfile
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from unittest.mock import patch

import data_designer.config as dd
import nemo_data_designer_plugin.testing.utils as u
import pandas as pd
import pytest
from data_designer.config.analysis.dataset_profiler import DatasetProfilerResults
from nemo_data_designer_plugin.jobs.run import BUFFER_SIZE
from nemo_data_designer_plugin.jobs.spec import DataDesignerJobConfig
from nemo_data_designer_plugin.jobs.task_results import ANALYSIS_RESULT_NAME, ARTIFACTS_RESULT_NAME


def _get_dataset(ctx: u.CreateJobTestContext, job_name: str) -> pd.DataFrame:
    with tempfile.TemporaryDirectory() as tmpdir:
        artifacts_download = ctx.sdk.jobs.results.download("artifacts", job=job_name)
        with tarfile.open(fileobj=io.BytesIO(artifacts_download.read()), mode="r:*") as tar:
            tar.extractall(path=tmpdir)
        return pd.read_parquet(f"{tmpdir}/artifacts/dataset/parquet-files")


def _get_analysis(ctx: u.CreateJobTestContext, job_name: str) -> DatasetProfilerResults:
    response = ctx.sdk.jobs.results.download("analysis", job=job_name)
    return DatasetProfilerResults.model_validate_json(response.read().decode())


@pytest.fixture
def _failing_result_manager() -> Generator[None]:
    with patch("nemo_platform_plugin.jobs.result_manager.ResultManager", u.FailingResultManager):
        yield


@pytest.mark.integration
@pytest.mark.asyncio
async def test_task() -> None:
    test_value = "test-value"
    num_records = 42
    builder = dd.DataDesignerConfigBuilder(model_configs=[u.make_model_config()])
    builder.add_column(
        column_config=dd.SamplerColumnConfig(
            name="foo", sampler_type=dd.SamplerType.CATEGORY, params=dd.CategorySamplerParams(values=[test_value])
        )
    )
    dd_job_config = DataDesignerJobConfig(num_records=num_records, config=builder.build())

    job_config = await u.compile_create_job(dd_job_config, workspace="default")
    job_name = "data-designer-abc123"

    async with u.task_context(job_config, job_name) as ctx:
        result = ctx.run_task()
        assert result.exit_code == 0

        results = ctx.sdk.jobs.results.list(job_name)
        assert len(results.data) == 2
        result_names = [r.name for r in results.data]
        assert ANALYSIS_RESULT_NAME in result_names
        assert ARTIFACTS_RESULT_NAME in result_names

        dataset = _get_dataset(ctx, job_name)
        expected_partial_data = pd.DataFrame(data={"foo": [test_value] * num_records})
        pd.testing.assert_frame_equal(dataset, expected_partial_data)

        analysis = _get_analysis(ctx, job_name)
        assert analysis.num_records == 42


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Batch-completion artifact saves are not yet available through the high-level library interfaces"
)
async def test_save_partial_dataset_on_failure(_failing_result_manager: None) -> None:
    test_value = "test-value"
    builder = dd.DataDesignerConfigBuilder(model_configs=[u.make_model_config()])
    builder.add_column(
        column_config=dd.SamplerColumnConfig(
            name="foo", sampler_type=dd.SamplerType.CATEGORY, params=dd.CategorySamplerParams(values=[test_value])
        )
    )

    requested_num_records = BUFFER_SIZE * (u.FAILING_RESULT_MANAGER_MAX_SUCCESSFUL_CALLS + 1)
    expected_num_records = BUFFER_SIZE * u.FAILING_RESULT_MANAGER_MAX_SUCCESSFUL_CALLS
    expected_partial_data = pd.DataFrame(data={"foo": [test_value] * expected_num_records})

    dd_job_config = DataDesignerJobConfig(num_records=requested_num_records, config=builder.build())
    job_config = await u.compile_create_job(dd_job_config, workspace="default")
    job_name = "data-designer-abc123"

    async with u.task_context(job_config, job_name) as ctx:
        result = ctx.run_task()
        assert result.exit_code == 1

        results = ctx.sdk.jobs.results.list(job_name)
        assert len(results.data) == 1
        result_names = [r.name for r in results.data]
        assert ANALYSIS_RESULT_NAME not in result_names
        assert ARTIFACTS_RESULT_NAME in result_names

        dataset = _get_dataset(ctx, job_name)
        pd.testing.assert_frame_equal(dataset, expected_partial_data)


@pytest.mark.asyncio
async def test_exiting_with_error() -> None:
    builder = dd.DataDesignerConfigBuilder(model_configs=[u.make_model_config()])
    builder.add_column(
        column_config=dd.SamplerColumnConfig(
            name="foo", sampler_type=dd.SamplerType.CATEGORY, params=dd.CategorySamplerParams(values=["a", "b"])
        )
    )
    dd_job_config = DataDesignerJobConfig(num_records=42, config=builder.build())
    job_config = await u.compile_create_job(dd_job_config)
    job_name = "data-designer-abc123"

    with (
        capture_job_log_messages() as log_messages,
        patch("nemo_data_designer_plugin.jobs.run.create_data_designer_context", side_effect=RuntimeError("Yuck")),
    ):
        async with u.task_context(job_config, job_name) as ctx:
            result = ctx.run_task()
            assert result.exit_code == 1
            assert any("Yuck" in message for message in log_messages)


@pytest.mark.asyncio
async def test_seed_dataset() -> None:
    builder = dd.DataDesignerConfigBuilder(model_configs=[u.make_model_config()])
    builder.with_seed_dataset(dd.HuggingFaceSeedSource(path="path/to/data.parquet"))
    builder.add_column(column_config=dd.ExpressionColumnConfig(name="full_name", expr=u.FULL_NAME_EXPR))
    dd_job_config = DataDesignerJobConfig(num_records=3, config=builder.build())

    job_config = await u.compile_create_job(dd_job_config)
    job_name = "data-designer-abc123"

    with u.mock_hf_seed_reader():
        async with u.task_context(job_config, job_name) as ctx:
            result = ctx.run_task()
            assert result.exit_code == 0
            dataset = _get_dataset(ctx, job_name)
            assert set(dataset["full_name"].values) == u.FULL_NAMES


class _MessageCaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.ERROR)
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


@contextmanager
def capture_job_log_messages() -> Iterator[list[str]]:
    job_logger = logging.getLogger("nemo_data_designer_plugin.jobs.run")
    previous_level = job_logger.level
    handler = _MessageCaptureHandler()

    job_logger.addHandler(handler)
    job_logger.setLevel(logging.ERROR)
    try:
        yield handler.messages
    finally:
        job_logger.removeHandler(handler)
        job_logger.setLevel(previous_level)
