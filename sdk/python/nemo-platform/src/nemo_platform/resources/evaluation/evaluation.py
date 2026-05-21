# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .metrics import (
    MetricsResource,
    AsyncMetricsResource,
    MetricsResourceWithRawResponse,
    AsyncMetricsResourceWithRawResponse,
    MetricsResourceWithStreamingResponse,
    AsyncMetricsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from .benchmarks import (
    BenchmarksResource,
    AsyncBenchmarksResource,
    BenchmarksResourceWithRawResponse,
    AsyncBenchmarksResourceWithRawResponse,
    BenchmarksResourceWithStreamingResponse,
    AsyncBenchmarksResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from .metric_job_results import (
    MetricJobResultsResource,
    AsyncMetricJobResultsResource,
    MetricJobResultsResourceWithRawResponse,
    AsyncMetricJobResultsResourceWithRawResponse,
    MetricJobResultsResourceWithStreamingResponse,
    AsyncMetricJobResultsResourceWithStreamingResponse,
)
from .benchmark_job_results import (
    BenchmarkJobResultsResource,
    AsyncBenchmarkJobResultsResource,
    BenchmarkJobResultsResourceWithRawResponse,
    AsyncBenchmarkJobResultsResourceWithRawResponse,
    BenchmarkJobResultsResourceWithStreamingResponse,
    AsyncBenchmarkJobResultsResourceWithStreamingResponse,
)
from .metric_jobs.metric_jobs import (
    MetricJobsResource,
    AsyncMetricJobsResource,
    MetricJobsResourceWithRawResponse,
    AsyncMetricJobsResourceWithRawResponse,
    MetricJobsResourceWithStreamingResponse,
    AsyncMetricJobsResourceWithStreamingResponse,
)
from .benchmark_jobs.benchmark_jobs import (
    BenchmarkJobsResource,
    AsyncBenchmarkJobsResource,
    BenchmarkJobsResourceWithRawResponse,
    AsyncBenchmarkJobsResourceWithRawResponse,
    BenchmarkJobsResourceWithStreamingResponse,
    AsyncBenchmarkJobsResourceWithStreamingResponse,
)

__all__ = ["EvaluationResource", "AsyncEvaluationResource"]


class EvaluationResource(SyncAPIResource):
    @cached_property
    def benchmarks(self) -> BenchmarksResource:
        return BenchmarksResource(self._client)

    @cached_property
    def benchmark_jobs(self) -> BenchmarkJobsResource:
        return BenchmarkJobsResource(self._client)

    @cached_property
    def benchmark_job_results(self) -> BenchmarkJobResultsResource:
        return BenchmarkJobResultsResource(self._client)

    @cached_property
    def metrics(self) -> MetricsResource:
        return MetricsResource(self._client)

    @cached_property
    def metric_jobs(self) -> MetricJobsResource:
        return MetricJobsResource(self._client)

    @cached_property
    def metric_job_results(self) -> MetricJobResultsResource:
        return MetricJobResultsResource(self._client)

    @cached_property
    def with_raw_response(self) -> EvaluationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return EvaluationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EvaluationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return EvaluationResourceWithStreamingResponse(self)


class AsyncEvaluationResource(AsyncAPIResource):
    @cached_property
    def benchmarks(self) -> AsyncBenchmarksResource:
        return AsyncBenchmarksResource(self._client)

    @cached_property
    def benchmark_jobs(self) -> AsyncBenchmarkJobsResource:
        return AsyncBenchmarkJobsResource(self._client)

    @cached_property
    def benchmark_job_results(self) -> AsyncBenchmarkJobResultsResource:
        return AsyncBenchmarkJobResultsResource(self._client)

    @cached_property
    def metrics(self) -> AsyncMetricsResource:
        return AsyncMetricsResource(self._client)

    @cached_property
    def metric_jobs(self) -> AsyncMetricJobsResource:
        return AsyncMetricJobsResource(self._client)

    @cached_property
    def metric_job_results(self) -> AsyncMetricJobResultsResource:
        return AsyncMetricJobResultsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEvaluationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncEvaluationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEvaluationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncEvaluationResourceWithStreamingResponse(self)


class EvaluationResourceWithRawResponse:
    def __init__(self, evaluation: EvaluationResource) -> None:
        self._evaluation = evaluation

    @cached_property
    def benchmarks(self) -> BenchmarksResourceWithRawResponse:
        return BenchmarksResourceWithRawResponse(self._evaluation.benchmarks)

    @cached_property
    def benchmark_jobs(self) -> BenchmarkJobsResourceWithRawResponse:
        return BenchmarkJobsResourceWithRawResponse(self._evaluation.benchmark_jobs)

    @cached_property
    def benchmark_job_results(self) -> BenchmarkJobResultsResourceWithRawResponse:
        return BenchmarkJobResultsResourceWithRawResponse(self._evaluation.benchmark_job_results)

    @cached_property
    def metrics(self) -> MetricsResourceWithRawResponse:
        return MetricsResourceWithRawResponse(self._evaluation.metrics)

    @cached_property
    def metric_jobs(self) -> MetricJobsResourceWithRawResponse:
        return MetricJobsResourceWithRawResponse(self._evaluation.metric_jobs)

    @cached_property
    def metric_job_results(self) -> MetricJobResultsResourceWithRawResponse:
        return MetricJobResultsResourceWithRawResponse(self._evaluation.metric_job_results)


class AsyncEvaluationResourceWithRawResponse:
    def __init__(self, evaluation: AsyncEvaluationResource) -> None:
        self._evaluation = evaluation

    @cached_property
    def benchmarks(self) -> AsyncBenchmarksResourceWithRawResponse:
        return AsyncBenchmarksResourceWithRawResponse(self._evaluation.benchmarks)

    @cached_property
    def benchmark_jobs(self) -> AsyncBenchmarkJobsResourceWithRawResponse:
        return AsyncBenchmarkJobsResourceWithRawResponse(self._evaluation.benchmark_jobs)

    @cached_property
    def benchmark_job_results(self) -> AsyncBenchmarkJobResultsResourceWithRawResponse:
        return AsyncBenchmarkJobResultsResourceWithRawResponse(self._evaluation.benchmark_job_results)

    @cached_property
    def metrics(self) -> AsyncMetricsResourceWithRawResponse:
        return AsyncMetricsResourceWithRawResponse(self._evaluation.metrics)

    @cached_property
    def metric_jobs(self) -> AsyncMetricJobsResourceWithRawResponse:
        return AsyncMetricJobsResourceWithRawResponse(self._evaluation.metric_jobs)

    @cached_property
    def metric_job_results(self) -> AsyncMetricJobResultsResourceWithRawResponse:
        return AsyncMetricJobResultsResourceWithRawResponse(self._evaluation.metric_job_results)


class EvaluationResourceWithStreamingResponse:
    def __init__(self, evaluation: EvaluationResource) -> None:
        self._evaluation = evaluation

    @cached_property
    def benchmarks(self) -> BenchmarksResourceWithStreamingResponse:
        return BenchmarksResourceWithStreamingResponse(self._evaluation.benchmarks)

    @cached_property
    def benchmark_jobs(self) -> BenchmarkJobsResourceWithStreamingResponse:
        return BenchmarkJobsResourceWithStreamingResponse(self._evaluation.benchmark_jobs)

    @cached_property
    def benchmark_job_results(self) -> BenchmarkJobResultsResourceWithStreamingResponse:
        return BenchmarkJobResultsResourceWithStreamingResponse(self._evaluation.benchmark_job_results)

    @cached_property
    def metrics(self) -> MetricsResourceWithStreamingResponse:
        return MetricsResourceWithStreamingResponse(self._evaluation.metrics)

    @cached_property
    def metric_jobs(self) -> MetricJobsResourceWithStreamingResponse:
        return MetricJobsResourceWithStreamingResponse(self._evaluation.metric_jobs)

    @cached_property
    def metric_job_results(self) -> MetricJobResultsResourceWithStreamingResponse:
        return MetricJobResultsResourceWithStreamingResponse(self._evaluation.metric_job_results)


class AsyncEvaluationResourceWithStreamingResponse:
    def __init__(self, evaluation: AsyncEvaluationResource) -> None:
        self._evaluation = evaluation

    @cached_property
    def benchmarks(self) -> AsyncBenchmarksResourceWithStreamingResponse:
        return AsyncBenchmarksResourceWithStreamingResponse(self._evaluation.benchmarks)

    @cached_property
    def benchmark_jobs(self) -> AsyncBenchmarkJobsResourceWithStreamingResponse:
        return AsyncBenchmarkJobsResourceWithStreamingResponse(self._evaluation.benchmark_jobs)

    @cached_property
    def benchmark_job_results(self) -> AsyncBenchmarkJobResultsResourceWithStreamingResponse:
        return AsyncBenchmarkJobResultsResourceWithStreamingResponse(self._evaluation.benchmark_job_results)

    @cached_property
    def metrics(self) -> AsyncMetricsResourceWithStreamingResponse:
        return AsyncMetricsResourceWithStreamingResponse(self._evaluation.metrics)

    @cached_property
    def metric_jobs(self) -> AsyncMetricJobsResourceWithStreamingResponse:
        return AsyncMetricJobsResourceWithStreamingResponse(self._evaluation.metric_jobs)

    @cached_property
    def metric_job_results(self) -> AsyncMetricJobResultsResourceWithStreamingResponse:
        return AsyncMetricJobResultsResourceWithStreamingResponse(self._evaluation.metric_job_results)
