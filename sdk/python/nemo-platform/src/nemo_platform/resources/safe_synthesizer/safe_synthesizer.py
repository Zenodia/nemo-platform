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

from ..._compat import cached_property
from .jobs.jobs import (
    JobsResource,
    AsyncJobsResource,
    JobsResourceWithRawResponse,
    AsyncJobsResourceWithRawResponse,
    JobsResourceWithStreamingResponse,
    AsyncJobsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["SafeSynthesizerResource", "AsyncSafeSynthesizerResource"]


class SafeSynthesizerResource(SyncAPIResource):
    @cached_property
    def jobs(self) -> JobsResource:
        return JobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> SafeSynthesizerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return SafeSynthesizerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SafeSynthesizerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return SafeSynthesizerResourceWithStreamingResponse(self)


class AsyncSafeSynthesizerResource(AsyncAPIResource):
    @cached_property
    def jobs(self) -> AsyncJobsResource:
        return AsyncJobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSafeSynthesizerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncSafeSynthesizerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSafeSynthesizerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncSafeSynthesizerResourceWithStreamingResponse(self)


class SafeSynthesizerResourceWithRawResponse:
    def __init__(self, safe_synthesizer: SafeSynthesizerResource) -> None:
        self._safe_synthesizer = safe_synthesizer

    @cached_property
    def jobs(self) -> JobsResourceWithRawResponse:
        return JobsResourceWithRawResponse(self._safe_synthesizer.jobs)


class AsyncSafeSynthesizerResourceWithRawResponse:
    def __init__(self, safe_synthesizer: AsyncSafeSynthesizerResource) -> None:
        self._safe_synthesizer = safe_synthesizer

    @cached_property
    def jobs(self) -> AsyncJobsResourceWithRawResponse:
        return AsyncJobsResourceWithRawResponse(self._safe_synthesizer.jobs)


class SafeSynthesizerResourceWithStreamingResponse:
    def __init__(self, safe_synthesizer: SafeSynthesizerResource) -> None:
        self._safe_synthesizer = safe_synthesizer

    @cached_property
    def jobs(self) -> JobsResourceWithStreamingResponse:
        return JobsResourceWithStreamingResponse(self._safe_synthesizer.jobs)


class AsyncSafeSynthesizerResourceWithStreamingResponse:
    def __init__(self, safe_synthesizer: AsyncSafeSynthesizerResource) -> None:
        self._safe_synthesizer = safe_synthesizer

    @cached_property
    def jobs(self) -> AsyncJobsResourceWithStreamingResponse:
        return AsyncJobsResourceWithStreamingResponse(self._safe_synthesizer.jobs)
