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

from typing import List
from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import path_template, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncDefaultPagination, AsyncDefaultPagination
from ..._base_client import AsyncPaginator, make_request_options
from ...types.evaluation import benchmark_job_result_list_params, benchmark_job_result_retrieve_params
from ...types.shared.delete_response import DeleteResponse
from ...types.evaluation.benchmark_job_result import BenchmarkJobResult

__all__ = ["BenchmarkJobResultsResource", "AsyncBenchmarkJobResultsResource"]


class BenchmarkJobResultsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BenchmarkJobResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return BenchmarkJobResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BenchmarkJobResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return BenchmarkJobResultsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        name: str,
        *,
        workspace: str | None = None,
        aggregate_fields: List[
            Literal[
                "nan_count",
                "sum",
                "mean",
                "min",
                "max",
                "std_dev",
                "variance",
                "score_type",
                "percentiles",
                "histogram",
                "rubric_distribution",
                "mode_category",
            ]
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BenchmarkJobResult:
        """
        Get a specific benchmark job result by workspace and job name.

        Args:
          aggregate_fields: Aggregate score fields to include in the response (comma-separated or repeated).
              Default: ('nan_count', 'sum', 'mean', 'min', 'max'). Available: ('nan_count',
              'sum', 'mean', 'min', 'max', 'std_dev', 'variance', 'score_type', 'percentiles',
              'histogram', 'rubric_distribution', 'mode_category').

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-job-results/{name}",
                workspace=workspace,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"aggregate_fields": aggregate_fields},
                    benchmark_job_result_retrieve_params.BenchmarkJobResultRetrieveParams,
                ),
            ),
            cast_to=BenchmarkJobResult,
        )

    def list(
        self,
        *,
        workspace: str | None = None,
        aggregate_fields: List[
            Literal[
                "nan_count",
                "sum",
                "mean",
                "min",
                "max",
                "std_dev",
                "variance",
                "score_type",
                "percentiles",
                "histogram",
                "rubric_distribution",
                "mode_category",
            ]
        ]
        | Omit = omit,
        filter: benchmark_job_result_list_params.Filter | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: Literal["-created_at", "created_at", "-updated_at", "updated_at", "-name", "name"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncDefaultPagination[BenchmarkJobResult]:
        """
        List stored evaluation results for benchmark jobs.

        Args:
          aggregate_fields: Aggregate score fields to include in the response (comma-separated or repeated).
              Default: ('nan_count', 'sum', 'mean', 'min', 'max'). Available: ('nan_count',
              'sum', 'mean', 'min', 'max', 'std_dev', 'variance', 'score_type', 'percentiles',
              'histogram', 'rubric_distribution', 'mode_category').

          filter: Filter benchmark job results by name, benchmark, metrics, dataset, model, and
              dates. Supports JSON filter syntax with operators: $eq, $like, $lt, $lte, $gt,
              $gte, $in, $nin, $and, $or, $not. Also supports text filter syntax.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        return self._get_api_list(
            path_template("/apis/evaluation/v2/workspaces/{workspace}/benchmark-job-results", workspace=workspace),
            page=SyncDefaultPagination[BenchmarkJobResult],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "aggregate_fields": aggregate_fields,
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    benchmark_job_result_list_params.BenchmarkJobResultListParams,
                ),
            ),
            model=BenchmarkJobResult,
        )

    def delete(
        self,
        name: str,
        *,
        workspace: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeleteResponse:
        """
        Delete an evaluation benchmark job result.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._delete(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-job-results/{name}",
                workspace=workspace,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncBenchmarkJobResultsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBenchmarkJobResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncBenchmarkJobResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBenchmarkJobResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncBenchmarkJobResultsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        name: str,
        *,
        workspace: str | None = None,
        aggregate_fields: List[
            Literal[
                "nan_count",
                "sum",
                "mean",
                "min",
                "max",
                "std_dev",
                "variance",
                "score_type",
                "percentiles",
                "histogram",
                "rubric_distribution",
                "mode_category",
            ]
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BenchmarkJobResult:
        """
        Get a specific benchmark job result by workspace and job name.

        Args:
          aggregate_fields: Aggregate score fields to include in the response (comma-separated or repeated).
              Default: ('nan_count', 'sum', 'mean', 'min', 'max'). Available: ('nan_count',
              'sum', 'mean', 'min', 'max', 'std_dev', 'variance', 'score_type', 'percentiles',
              'histogram', 'rubric_distribution', 'mode_category').

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-job-results/{name}",
                workspace=workspace,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"aggregate_fields": aggregate_fields},
                    benchmark_job_result_retrieve_params.BenchmarkJobResultRetrieveParams,
                ),
            ),
            cast_to=BenchmarkJobResult,
        )

    def list(
        self,
        *,
        workspace: str | None = None,
        aggregate_fields: List[
            Literal[
                "nan_count",
                "sum",
                "mean",
                "min",
                "max",
                "std_dev",
                "variance",
                "score_type",
                "percentiles",
                "histogram",
                "rubric_distribution",
                "mode_category",
            ]
        ]
        | Omit = omit,
        filter: benchmark_job_result_list_params.Filter | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: Literal["-created_at", "created_at", "-updated_at", "updated_at", "-name", "name"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[BenchmarkJobResult, AsyncDefaultPagination[BenchmarkJobResult]]:
        """
        List stored evaluation results for benchmark jobs.

        Args:
          aggregate_fields: Aggregate score fields to include in the response (comma-separated or repeated).
              Default: ('nan_count', 'sum', 'mean', 'min', 'max'). Available: ('nan_count',
              'sum', 'mean', 'min', 'max', 'std_dev', 'variance', 'score_type', 'percentiles',
              'histogram', 'rubric_distribution', 'mode_category').

          filter: Filter benchmark job results by name, benchmark, metrics, dataset, model, and
              dates. Supports JSON filter syntax with operators: $eq, $like, $lt, $lte, $gt,
              $gte, $in, $nin, $and, $or, $not. Also supports text filter syntax.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        return self._get_api_list(
            path_template("/apis/evaluation/v2/workspaces/{workspace}/benchmark-job-results", workspace=workspace),
            page=AsyncDefaultPagination[BenchmarkJobResult],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "aggregate_fields": aggregate_fields,
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    benchmark_job_result_list_params.BenchmarkJobResultListParams,
                ),
            ),
            model=BenchmarkJobResult,
        )

    async def delete(
        self,
        name: str,
        *,
        workspace: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeleteResponse:
        """
        Delete an evaluation benchmark job result.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._delete(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-job-results/{name}",
                workspace=workspace,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class BenchmarkJobResultsResourceWithRawResponse:
    def __init__(self, benchmark_job_results: BenchmarkJobResultsResource) -> None:
        self._benchmark_job_results = benchmark_job_results

        self.retrieve = to_raw_response_wrapper(
            benchmark_job_results.retrieve,
        )
        self.list = to_raw_response_wrapper(
            benchmark_job_results.list,
        )
        self.delete = to_raw_response_wrapper(
            benchmark_job_results.delete,
        )


class AsyncBenchmarkJobResultsResourceWithRawResponse:
    def __init__(self, benchmark_job_results: AsyncBenchmarkJobResultsResource) -> None:
        self._benchmark_job_results = benchmark_job_results

        self.retrieve = async_to_raw_response_wrapper(
            benchmark_job_results.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            benchmark_job_results.list,
        )
        self.delete = async_to_raw_response_wrapper(
            benchmark_job_results.delete,
        )


class BenchmarkJobResultsResourceWithStreamingResponse:
    def __init__(self, benchmark_job_results: BenchmarkJobResultsResource) -> None:
        self._benchmark_job_results = benchmark_job_results

        self.retrieve = to_streamed_response_wrapper(
            benchmark_job_results.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            benchmark_job_results.list,
        )
        self.delete = to_streamed_response_wrapper(
            benchmark_job_results.delete,
        )


class AsyncBenchmarkJobResultsResourceWithStreamingResponse:
    def __init__(self, benchmark_job_results: AsyncBenchmarkJobResultsResource) -> None:
        self._benchmark_job_results = benchmark_job_results

        self.retrieve = async_to_streamed_response_wrapper(
            benchmark_job_results.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            benchmark_job_results.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            benchmark_job_results.delete,
        )
