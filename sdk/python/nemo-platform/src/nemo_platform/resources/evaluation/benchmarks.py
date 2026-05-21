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

from typing import Any, Dict, cast
from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
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
from ...types.evaluation import (
    FilesetRef,
    benchmark_list_params,
    benchmark_create_params,
    benchmark_retrieve_params,
)
from ...types.evaluation.metric_ref import MetricRef
from ...types.evaluation.fileset_ref import FilesetRef
from ...types.shared.delete_response import DeleteResponse
from ...types.evaluation.field_mapping_param import FieldMappingParam
from ...types.evaluation.benchmarks_list_response import Data
from ...types.evaluation.benchmark_create_response import BenchmarkCreateResponse
from ...types.evaluation.benchmark_retrieve_response import BenchmarkRetrieveResponse
from ..._exceptions import ConflictError

__all__ = ["BenchmarksResource", "AsyncBenchmarksResource"]


class BenchmarksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BenchmarksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return BenchmarksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BenchmarksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return BenchmarksResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        workspace: str | None = None,
        dataset: FilesetRef,
        description: str,
        metrics: SequenceNotStr[MetricRef],
        name: str,
        extended_response: bool | Omit = omit,
        field_mapping: FieldMappingParam | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BenchmarkCreateResponse:
        """
        Create a new custom evaluation benchmark.

        Benchmarks can be reused across multiple evaluations. The benchmark type
        determines the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          dataset: Reference to a Fileset in the Files API.

              A reference is a string with format 'workspace/fileset-name' that points to a
              persisted fileset entity. When used as a dataset source, all files within the
              fileset will be downloaded to the job container.

              See [Entity references](docs/get-started/concepts/entity-references.md) for the
              general entity reference pattern used across the platform.

          description: The description of the benchmark.

          metrics: The metrics that comprise this benchmark (format: workspace/metric_name).

          name: The name of the benchmark.

          extended_response: Whether to return the extended benchmark.

          field_mapping:
              Maps canonical evaluator fields to raw dataset column paths. Example: {'input':
              'question', 'output': 'answer', 'reference': 'gold', 'trajectory': 'steps'}

          labels: Labels are key-value pairs that can be used for grouping and filtering.


          exist_ok: Do not raise an error if the resource already exists. Returns the existing resource.


          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        try:
            if workspace is None:
                workspace = self._client._get_workspace_path_param()
            if not workspace:
                raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
            return cast(
                BenchmarkCreateResponse,
                self._post(
                    path_template("/apis/evaluation/v2/workspaces/{workspace}/benchmarks", workspace=workspace),
                    body=maybe_transform(
                        {
                            "dataset": dataset,
                            "description": description,
                            "metrics": metrics,
                            "name": name,
                            "field_mapping": field_mapping,
                            "labels": labels,
                        },
                        benchmark_create_params.BenchmarkCreateParams,
                    ),
                    options=make_request_options(
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        extra_body=extra_body,
                        timeout=timeout,
                        query=maybe_transform(
                            {"extended_response": extended_response}, benchmark_create_params.BenchmarkCreateParams
                        ),
                    ),
                    cast_to=cast(
                        Any, BenchmarkCreateResponse
                    ),  # Union types cannot be passed in as arguments in the type system
                ),
            )
        except ConflictError:
            if not exist_ok:
                raise
            return self.retrieve(name = name, workspace = workspace)

    def retrieve(
        self,
        name: str,
        *,
        workspace: str | None = None,
        extended_response: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BenchmarkRetrieveResponse:
        """
        Get a specific evaluation benchmark by workspace and benchmark name.

        Args:
          extended_response: Whether to return the extended benchmark.

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
        return cast(
            BenchmarkRetrieveResponse,
            self._get(
                path_template(
                    "/apis/evaluation/v2/workspaces/{workspace}/benchmarks/{name}", workspace=workspace, name=name
                ),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=maybe_transform(
                        {"extended_response": extended_response}, benchmark_retrieve_params.BenchmarkRetrieveParams
                    ),
                ),
                cast_to=cast(
                    Any, BenchmarkRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        *,
        workspace: str | None = None,
        extended_response: bool | Omit = omit,
        filter: benchmark_list_params.Filter | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: Literal["-created_at", "created_at", "-updated_at", "updated_at", "-name", "name"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncDefaultPagination[Data]:
        """
        List all available evaluation benchmarks.

        Args:
          extended_response: Whether to return the extended benchmark.

          filter: Filter benchmarks by name, description, dataset, project, and dates. Supports
              JSON filter syntax with operators: $eq, $like, $lt, $lte, $gt, $gte, $in, $nin,
              $and, $or, $not. Also supports text filter syntax.

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
            path_template("/apis/evaluation/v2/workspaces/{workspace}/benchmarks", workspace=workspace),
            page=SyncDefaultPagination[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "extended_response": extended_response,
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    benchmark_list_params.BenchmarkListParams,
                ),
            ),
            model=cast(Any, Data),  # Union types cannot be passed in as arguments in the type system
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
        """Delete a custom evaluation benchmark.

        Predefined benchmarks cannot be deleted.

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
                "/apis/evaluation/v2/workspaces/{workspace}/benchmarks/{name}", workspace=workspace, name=name
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncBenchmarksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBenchmarksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncBenchmarksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBenchmarksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncBenchmarksResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        workspace: str | None = None,
        dataset: FilesetRef,
        description: str,
        metrics: SequenceNotStr[MetricRef],
        name: str,
        extended_response: bool | Omit = omit,
        field_mapping: FieldMappingParam | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BenchmarkCreateResponse:
        """
        Create a new custom evaluation benchmark.

        Benchmarks can be reused across multiple evaluations. The benchmark type
        determines the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          dataset: Reference to a Fileset in the Files API.

              A reference is a string with format 'workspace/fileset-name' that points to a
              persisted fileset entity. When used as a dataset source, all files within the
              fileset will be downloaded to the job container.

              See [Entity references](docs/get-started/concepts/entity-references.md) for the
              general entity reference pattern used across the platform.

          description: The description of the benchmark.

          metrics: The metrics that comprise this benchmark (format: workspace/metric_name).

          name: The name of the benchmark.

          extended_response: Whether to return the extended benchmark.

          field_mapping:
              Maps canonical evaluator fields to raw dataset column paths. Example: {'input':
              'question', 'output': 'answer', 'reference': 'gold', 'trajectory': 'steps'}

          labels: Labels are key-value pairs that can be used for grouping and filtering.


          exist_ok: Do not raise an error if the resource already exists. Returns the existing resource.


          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        try:
            if workspace is None:
                workspace = self._client._get_workspace_path_param()
            if not workspace:
                raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
            return cast(
                BenchmarkCreateResponse,
                await self._post(
                    path_template("/apis/evaluation/v2/workspaces/{workspace}/benchmarks", workspace=workspace),
                    body=await async_maybe_transform(
                        {
                            "dataset": dataset,
                            "description": description,
                            "metrics": metrics,
                            "name": name,
                            "field_mapping": field_mapping,
                            "labels": labels,
                        },
                        benchmark_create_params.BenchmarkCreateParams,
                    ),
                    options=make_request_options(
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        extra_body=extra_body,
                        timeout=timeout,
                        query=await async_maybe_transform(
                            {"extended_response": extended_response}, benchmark_create_params.BenchmarkCreateParams
                        ),
                    ),
                    cast_to=cast(
                        Any, BenchmarkCreateResponse
                    ),  # Union types cannot be passed in as arguments in the type system
                ),
            )
        except ConflictError:
            if not exist_ok:
                raise
            return await self.retrieve(name = name, workspace = workspace)

    async def retrieve(
        self,
        name: str,
        *,
        workspace: str | None = None,
        extended_response: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BenchmarkRetrieveResponse:
        """
        Get a specific evaluation benchmark by workspace and benchmark name.

        Args:
          extended_response: Whether to return the extended benchmark.

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
        return cast(
            BenchmarkRetrieveResponse,
            await self._get(
                path_template(
                    "/apis/evaluation/v2/workspaces/{workspace}/benchmarks/{name}", workspace=workspace, name=name
                ),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=await async_maybe_transform(
                        {"extended_response": extended_response}, benchmark_retrieve_params.BenchmarkRetrieveParams
                    ),
                ),
                cast_to=cast(
                    Any, BenchmarkRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        *,
        workspace: str | None = None,
        extended_response: bool | Omit = omit,
        filter: benchmark_list_params.Filter | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: Literal["-created_at", "created_at", "-updated_at", "updated_at", "-name", "name"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Data, AsyncDefaultPagination[Data]]:
        """
        List all available evaluation benchmarks.

        Args:
          extended_response: Whether to return the extended benchmark.

          filter: Filter benchmarks by name, description, dataset, project, and dates. Supports
              JSON filter syntax with operators: $eq, $like, $lt, $lte, $gt, $gte, $in, $nin,
              $and, $or, $not. Also supports text filter syntax.

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
            path_template("/apis/evaluation/v2/workspaces/{workspace}/benchmarks", workspace=workspace),
            page=AsyncDefaultPagination[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "extended_response": extended_response,
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    benchmark_list_params.BenchmarkListParams,
                ),
            ),
            model=cast(Any, Data),  # Union types cannot be passed in as arguments in the type system
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
        """Delete a custom evaluation benchmark.

        Predefined benchmarks cannot be deleted.

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
                "/apis/evaluation/v2/workspaces/{workspace}/benchmarks/{name}", workspace=workspace, name=name
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class BenchmarksResourceWithRawResponse:
    def __init__(self, benchmarks: BenchmarksResource) -> None:
        self._benchmarks = benchmarks

        self.create = to_raw_response_wrapper(
            benchmarks.create,
        )
        self.retrieve = to_raw_response_wrapper(
            benchmarks.retrieve,
        )
        self.list = to_raw_response_wrapper(
            benchmarks.list,
        )
        self.delete = to_raw_response_wrapper(
            benchmarks.delete,
        )


class AsyncBenchmarksResourceWithRawResponse:
    def __init__(self, benchmarks: AsyncBenchmarksResource) -> None:
        self._benchmarks = benchmarks

        self.create = async_to_raw_response_wrapper(
            benchmarks.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            benchmarks.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            benchmarks.list,
        )
        self.delete = async_to_raw_response_wrapper(
            benchmarks.delete,
        )


class BenchmarksResourceWithStreamingResponse:
    def __init__(self, benchmarks: BenchmarksResource) -> None:
        self._benchmarks = benchmarks

        self.create = to_streamed_response_wrapper(
            benchmarks.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            benchmarks.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            benchmarks.list,
        )
        self.delete = to_streamed_response_wrapper(
            benchmarks.delete,
        )


class AsyncBenchmarksResourceWithStreamingResponse:
    def __init__(self, benchmarks: AsyncBenchmarksResource) -> None:
        self._benchmarks = benchmarks

        self.create = async_to_streamed_response_wrapper(
            benchmarks.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            benchmarks.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            benchmarks.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            benchmarks.delete,
        )
