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

from typing import Dict

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ...._utils import path_template, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....pagination import SyncLogsPagination, AsyncLogsPagination, SyncDefaultPagination, AsyncDefaultPagination
from ...._base_client import AsyncPaginator, make_request_options
from .results.results import (
    ResultsResource,
    AsyncResultsResource,
    ResultsResourceWithRawResponse,
    AsyncResultsResourceWithRawResponse,
    ResultsResourceWithStreamingResponse,
    AsyncResultsResourceWithStreamingResponse,
)
from ....types.evaluation import (
    BenchmarkEvaluationJobsSortField,
    benchmark_job_list_params,
    benchmark_job_create_params,
    benchmark_job_get_logs_params,
)
from ....types.shared.platform_job_log import PlatformJobLog
from ....types.evaluation.benchmark_evaluation_job import BenchmarkEvaluationJob
from ....types.shared.platform_job_status_response import PlatformJobStatusResponse
from ....types.evaluation.benchmark_evaluation_jobs_sort_field import BenchmarkEvaluationJobsSortField
from ....types.evaluation.benchmark_evaluation_jobs_list_filter_param import BenchmarkEvaluationJobsListFilterParam

__all__ = ["BenchmarkJobsResource", "AsyncBenchmarkJobsResource"]


class BenchmarkJobsResource(SyncAPIResource):
    @cached_property
    def results(self) -> ResultsResource:
        return ResultsResource(self._client)

    @cached_property
    def with_raw_response(self) -> BenchmarkJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return BenchmarkJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BenchmarkJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return BenchmarkJobsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        workspace: str | None = None,
        spec: benchmark_job_create_params.Spec,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        ownership: Dict[str, object] | Omit = omit,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BenchmarkEvaluationJob:
        """
        Create Job

        Args:
          spec: Input for an offline benchmark evaluation job.

              Evaluates the benchmark's dataset against all metrics in the benchmark.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        return self._post(
            path_template("/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs", workspace=workspace),
            body=maybe_transform(
                {
                    "spec": spec,
                    "custom_fields": custom_fields,
                    "description": description,
                    "name": name,
                    "ownership": ownership,
                    "project": project,
                },
                benchmark_job_create_params.BenchmarkJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BenchmarkEvaluationJob,
        )

    def retrieve(
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
    ) -> BenchmarkEvaluationJob:
        """
        Get Job

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
        return self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}", workspace=workspace, name=name
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BenchmarkEvaluationJob,
        )

    def list(
        self,
        *,
        workspace: str | None = None,
        filter: BenchmarkEvaluationJobsListFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: BenchmarkEvaluationJobsSortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncDefaultPagination[BenchmarkEvaluationJob]:
        """
        List Jobs

        Args:
          filter: Filter jobs on various criteria.

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
            path_template("/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs", workspace=workspace),
            page=SyncDefaultPagination[BenchmarkEvaluationJob],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    benchmark_job_list_params.BenchmarkJobListParams,
                ),
            ),
            model=BenchmarkEvaluationJob,
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
    ) -> None:
        """
        Delete Job

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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}", workspace=workspace, name=name
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def cancel(
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
    ) -> BenchmarkEvaluationJob:
        """
        Cancel Job

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
        return self._post(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}/cancel",
                workspace=workspace,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BenchmarkEvaluationJob,
        )

    def get_logs(
        self,
        name: str,
        *,
        workspace: str | None = None,
        limit: int | Omit = omit,
        page_cursor: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncLogsPagination[PlatformJobLog]:
        """
        Get Job Logs

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
        return self._get_api_list(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}/logs", workspace=workspace, name=name
            ),
            page=SyncLogsPagination[PlatformJobLog],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "page_cursor": page_cursor,
                    },
                    benchmark_job_get_logs_params.BenchmarkJobGetLogsParams,
                ),
            ),
            model=PlatformJobLog,
        )

    def get_status(
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
    ) -> PlatformJobStatusResponse:
        """
        Get Job Status

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
        return self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}/status",
                workspace=workspace,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobStatusResponse,
        )


class AsyncBenchmarkJobsResource(AsyncAPIResource):
    @cached_property
    def results(self) -> AsyncResultsResource:
        return AsyncResultsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncBenchmarkJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncBenchmarkJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBenchmarkJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncBenchmarkJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        workspace: str | None = None,
        spec: benchmark_job_create_params.Spec,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        ownership: Dict[str, object] | Omit = omit,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BenchmarkEvaluationJob:
        """
        Create Job

        Args:
          spec: Input for an offline benchmark evaluation job.

              Evaluates the benchmark's dataset against all metrics in the benchmark.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        return await self._post(
            path_template("/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs", workspace=workspace),
            body=await async_maybe_transform(
                {
                    "spec": spec,
                    "custom_fields": custom_fields,
                    "description": description,
                    "name": name,
                    "ownership": ownership,
                    "project": project,
                },
                benchmark_job_create_params.BenchmarkJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BenchmarkEvaluationJob,
        )

    async def retrieve(
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
    ) -> BenchmarkEvaluationJob:
        """
        Get Job

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
        return await self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}", workspace=workspace, name=name
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BenchmarkEvaluationJob,
        )

    def list(
        self,
        *,
        workspace: str | None = None,
        filter: BenchmarkEvaluationJobsListFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: BenchmarkEvaluationJobsSortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[BenchmarkEvaluationJob, AsyncDefaultPagination[BenchmarkEvaluationJob]]:
        """
        List Jobs

        Args:
          filter: Filter jobs on various criteria.

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
            path_template("/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs", workspace=workspace),
            page=AsyncDefaultPagination[BenchmarkEvaluationJob],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    benchmark_job_list_params.BenchmarkJobListParams,
                ),
            ),
            model=BenchmarkEvaluationJob,
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
    ) -> None:
        """
        Delete Job

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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}", workspace=workspace, name=name
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def cancel(
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
    ) -> BenchmarkEvaluationJob:
        """
        Cancel Job

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
        return await self._post(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}/cancel",
                workspace=workspace,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BenchmarkEvaluationJob,
        )

    def get_logs(
        self,
        name: str,
        *,
        workspace: str | None = None,
        limit: int | Omit = omit,
        page_cursor: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[PlatformJobLog, AsyncLogsPagination[PlatformJobLog]]:
        """
        Get Job Logs

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
        return self._get_api_list(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}/logs", workspace=workspace, name=name
            ),
            page=AsyncLogsPagination[PlatformJobLog],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "page_cursor": page_cursor,
                    },
                    benchmark_job_get_logs_params.BenchmarkJobGetLogsParams,
                ),
            ),
            model=PlatformJobLog,
        )

    async def get_status(
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
    ) -> PlatformJobStatusResponse:
        """
        Get Job Status

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
        return await self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}/status",
                workspace=workspace,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobStatusResponse,
        )


class BenchmarkJobsResourceWithRawResponse:
    def __init__(self, benchmark_jobs: BenchmarkJobsResource) -> None:
        self._benchmark_jobs = benchmark_jobs

        self.create = to_raw_response_wrapper(
            benchmark_jobs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            benchmark_jobs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            benchmark_jobs.list,
        )
        self.delete = to_raw_response_wrapper(
            benchmark_jobs.delete,
        )
        self.cancel = to_raw_response_wrapper(
            benchmark_jobs.cancel,
        )
        self.get_logs = to_raw_response_wrapper(
            benchmark_jobs.get_logs,
        )
        self.get_status = to_raw_response_wrapper(
            benchmark_jobs.get_status,
        )

    @cached_property
    def results(self) -> ResultsResourceWithRawResponse:
        return ResultsResourceWithRawResponse(self._benchmark_jobs.results)


class AsyncBenchmarkJobsResourceWithRawResponse:
    def __init__(self, benchmark_jobs: AsyncBenchmarkJobsResource) -> None:
        self._benchmark_jobs = benchmark_jobs

        self.create = async_to_raw_response_wrapper(
            benchmark_jobs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            benchmark_jobs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            benchmark_jobs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            benchmark_jobs.delete,
        )
        self.cancel = async_to_raw_response_wrapper(
            benchmark_jobs.cancel,
        )
        self.get_logs = async_to_raw_response_wrapper(
            benchmark_jobs.get_logs,
        )
        self.get_status = async_to_raw_response_wrapper(
            benchmark_jobs.get_status,
        )

    @cached_property
    def results(self) -> AsyncResultsResourceWithRawResponse:
        return AsyncResultsResourceWithRawResponse(self._benchmark_jobs.results)


class BenchmarkJobsResourceWithStreamingResponse:
    def __init__(self, benchmark_jobs: BenchmarkJobsResource) -> None:
        self._benchmark_jobs = benchmark_jobs

        self.create = to_streamed_response_wrapper(
            benchmark_jobs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            benchmark_jobs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            benchmark_jobs.list,
        )
        self.delete = to_streamed_response_wrapper(
            benchmark_jobs.delete,
        )
        self.cancel = to_streamed_response_wrapper(
            benchmark_jobs.cancel,
        )
        self.get_logs = to_streamed_response_wrapper(
            benchmark_jobs.get_logs,
        )
        self.get_status = to_streamed_response_wrapper(
            benchmark_jobs.get_status,
        )

    @cached_property
    def results(self) -> ResultsResourceWithStreamingResponse:
        return ResultsResourceWithStreamingResponse(self._benchmark_jobs.results)


class AsyncBenchmarkJobsResourceWithStreamingResponse:
    def __init__(self, benchmark_jobs: AsyncBenchmarkJobsResource) -> None:
        self._benchmark_jobs = benchmark_jobs

        self.create = async_to_streamed_response_wrapper(
            benchmark_jobs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            benchmark_jobs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            benchmark_jobs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            benchmark_jobs.delete,
        )
        self.cancel = async_to_streamed_response_wrapper(
            benchmark_jobs.cancel,
        )
        self.get_logs = async_to_streamed_response_wrapper(
            benchmark_jobs.get_logs,
        )
        self.get_status = async_to_streamed_response_wrapper(
            benchmark_jobs.get_status,
        )

    @cached_property
    def results(self) -> AsyncResultsResourceWithStreamingResponse:
        return AsyncResultsResourceWithStreamingResponse(self._benchmark_jobs.results)
