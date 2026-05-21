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

from ....._types import Body, Query, Headers, NotGiven, not_given
from ....._utils import path_template
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.evaluation.aggregated_metric_result import AggregatedMetricResult

__all__ = ["AggregateScoresResource", "AsyncAggregateScoresResource"]


class AggregateScoresResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AggregateScoresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AggregateScoresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AggregateScoresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AggregateScoresResourceWithStreamingResponse(self)

    def download(
        self,
        job: str,
        *,
        workspace: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AggregatedMetricResult:
        """
        Download Job Result Aggregate-Scores

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
        return self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/metric-jobs/{job}/results/aggregate-scores/download",
                workspace=workspace,
                job=job,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AggregatedMetricResult,
        )


class AsyncAggregateScoresResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAggregateScoresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncAggregateScoresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAggregateScoresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncAggregateScoresResourceWithStreamingResponse(self)

    async def download(
        self,
        job: str,
        *,
        workspace: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AggregatedMetricResult:
        """
        Download Job Result Aggregate-Scores

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
        return await self._get(
            path_template(
                "/apis/evaluation/v2/workspaces/{workspace}/metric-jobs/{job}/results/aggregate-scores/download",
                workspace=workspace,
                job=job,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AggregatedMetricResult,
        )


class AggregateScoresResourceWithRawResponse:
    def __init__(self, aggregate_scores: AggregateScoresResource) -> None:
        self._aggregate_scores = aggregate_scores

        self.download = to_raw_response_wrapper(
            aggregate_scores.download,
        )


class AsyncAggregateScoresResourceWithRawResponse:
    def __init__(self, aggregate_scores: AsyncAggregateScoresResource) -> None:
        self._aggregate_scores = aggregate_scores

        self.download = async_to_raw_response_wrapper(
            aggregate_scores.download,
        )


class AggregateScoresResourceWithStreamingResponse:
    def __init__(self, aggregate_scores: AggregateScoresResource) -> None:
        self._aggregate_scores = aggregate_scores

        self.download = to_streamed_response_wrapper(
            aggregate_scores.download,
        )


class AsyncAggregateScoresResourceWithStreamingResponse:
    def __init__(self, aggregate_scores: AsyncAggregateScoresResource) -> None:
        self._aggregate_scores = aggregate_scores

        self.download = async_to_streamed_response_wrapper(
            aggregate_scores.download,
        )
