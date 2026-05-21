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

import httpx

from .artifacts import (
    ArtifactsResource,
    AsyncArtifactsResource,
    ArtifactsResourceWithRawResponse,
    AsyncArtifactsResourceWithRawResponse,
    ArtifactsResourceWithStreamingResponse,
    AsyncArtifactsResourceWithStreamingResponse,
)
from ....._types import Body, Query, Headers, NotGiven, not_given
from ....._utils import path_template
from .row_scores import (
    RowScoresResource,
    AsyncRowScoresResource,
    RowScoresResourceWithRawResponse,
    AsyncRowScoresResourceWithRawResponse,
    RowScoresResourceWithStreamingResponse,
    AsyncRowScoresResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .aggregate_scores import (
    AggregateScoresResource,
    AsyncAggregateScoresResource,
    AggregateScoresResourceWithRawResponse,
    AsyncAggregateScoresResourceWithRawResponse,
    AggregateScoresResourceWithStreamingResponse,
    AsyncAggregateScoresResourceWithStreamingResponse,
)
from .....types.shared.platform_job_result_response import PlatformJobResultResponse
from .....types.shared.platform_job_list_result_response import PlatformJobListResultResponse

__all__ = ["ResultsResource", "AsyncResultsResource"]


class ResultsResource(SyncAPIResource):
    @cached_property
    def aggregate_scores(self) -> AggregateScoresResource:
        return AggregateScoresResource(self._client)

    @cached_property
    def row_scores(self) -> RowScoresResource:
        return RowScoresResource(self._client)

    @cached_property
    def artifacts(self) -> ArtifactsResource:
        return ArtifactsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return ResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return ResultsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        name: str,
        *,
        workspace: str | None = None,
        job: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobResultResponse:
        """
        Get Job Result

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
        if not job:
            raise ValueError(f"Expected a non-empty value for `job` but received {job!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{job}/results/{name}",
                workspace=workspace,
                job=job,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobResultResponse,
        )

    def list(
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
    ) -> PlatformJobListResultResponse:
        """
        List Job Results

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
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}/results",
                workspace=workspace,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobListResultResponse,
        )

    def download(
        self,
        name: str,
        *,
        workspace: str | None = None,
        job: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BinaryAPIResponse:
        """
        Download Job Result

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
        if not job:
            raise ValueError(f"Expected a non-empty value for `job` but received {job!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{job}/results/{name}/download",
                workspace=workspace,
                job=job,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )


class AsyncResultsResource(AsyncAPIResource):
    @cached_property
    def aggregate_scores(self) -> AsyncAggregateScoresResource:
        return AsyncAggregateScoresResource(self._client)

    @cached_property
    def row_scores(self) -> AsyncRowScoresResource:
        return AsyncRowScoresResource(self._client)

    @cached_property
    def artifacts(self) -> AsyncArtifactsResource:
        return AsyncArtifactsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncResultsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        name: str,
        *,
        workspace: str | None = None,
        job: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobResultResponse:
        """
        Get Job Result

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
        if not job:
            raise ValueError(f"Expected a non-empty value for `job` but received {job!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{job}/results/{name}",
                workspace=workspace,
                job=job,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobResultResponse,
        )

    async def list(
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
    ) -> PlatformJobListResultResponse:
        """
        List Job Results

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
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{name}/results",
                workspace=workspace,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobListResultResponse,
        )

    async def download(
        self,
        name: str,
        *,
        workspace: str | None = None,
        job: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncBinaryAPIResponse:
        """
        Download Job Result

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
        if not job:
            raise ValueError(f"Expected a non-empty value for `job` but received {job!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/benchmark-jobs/{job}/results/{name}/download",
                workspace=workspace,
                job=job,
                name=name,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class ResultsResourceWithRawResponse:
    def __init__(self, results: ResultsResource) -> None:
        self._results = results

        self.retrieve = to_raw_response_wrapper(
            results.retrieve,
        )
        self.list = to_raw_response_wrapper(
            results.list,
        )
        self.download = to_custom_raw_response_wrapper(
            results.download,
            BinaryAPIResponse,
        )

    @cached_property
    def aggregate_scores(self) -> AggregateScoresResourceWithRawResponse:
        return AggregateScoresResourceWithRawResponse(self._results.aggregate_scores)

    @cached_property
    def row_scores(self) -> RowScoresResourceWithRawResponse:
        return RowScoresResourceWithRawResponse(self._results.row_scores)

    @cached_property
    def artifacts(self) -> ArtifactsResourceWithRawResponse:
        return ArtifactsResourceWithRawResponse(self._results.artifacts)


class AsyncResultsResourceWithRawResponse:
    def __init__(self, results: AsyncResultsResource) -> None:
        self._results = results

        self.retrieve = async_to_raw_response_wrapper(
            results.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            results.list,
        )
        self.download = async_to_custom_raw_response_wrapper(
            results.download,
            AsyncBinaryAPIResponse,
        )

    @cached_property
    def aggregate_scores(self) -> AsyncAggregateScoresResourceWithRawResponse:
        return AsyncAggregateScoresResourceWithRawResponse(self._results.aggregate_scores)

    @cached_property
    def row_scores(self) -> AsyncRowScoresResourceWithRawResponse:
        return AsyncRowScoresResourceWithRawResponse(self._results.row_scores)

    @cached_property
    def artifacts(self) -> AsyncArtifactsResourceWithRawResponse:
        return AsyncArtifactsResourceWithRawResponse(self._results.artifacts)


class ResultsResourceWithStreamingResponse:
    def __init__(self, results: ResultsResource) -> None:
        self._results = results

        self.retrieve = to_streamed_response_wrapper(
            results.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            results.list,
        )
        self.download = to_custom_streamed_response_wrapper(
            results.download,
            StreamedBinaryAPIResponse,
        )

    @cached_property
    def aggregate_scores(self) -> AggregateScoresResourceWithStreamingResponse:
        return AggregateScoresResourceWithStreamingResponse(self._results.aggregate_scores)

    @cached_property
    def row_scores(self) -> RowScoresResourceWithStreamingResponse:
        return RowScoresResourceWithStreamingResponse(self._results.row_scores)

    @cached_property
    def artifacts(self) -> ArtifactsResourceWithStreamingResponse:
        return ArtifactsResourceWithStreamingResponse(self._results.artifacts)


class AsyncResultsResourceWithStreamingResponse:
    def __init__(self, results: AsyncResultsResource) -> None:
        self._results = results

        self.retrieve = async_to_streamed_response_wrapper(
            results.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            results.list,
        )
        self.download = async_to_custom_streamed_response_wrapper(
            results.download,
            AsyncStreamedBinaryAPIResponse,
        )

    @cached_property
    def aggregate_scores(self) -> AsyncAggregateScoresResourceWithStreamingResponse:
        return AsyncAggregateScoresResourceWithStreamingResponse(self._results.aggregate_scores)

    @cached_property
    def row_scores(self) -> AsyncRowScoresResourceWithStreamingResponse:
        return AsyncRowScoresResourceWithStreamingResponse(self._results.row_scores)

    @cached_property
    def artifacts(self) -> AsyncArtifactsResourceWithStreamingResponse:
        return AsyncArtifactsResourceWithStreamingResponse(self._results.artifacts)
