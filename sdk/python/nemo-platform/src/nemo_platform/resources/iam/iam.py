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
from ..._resource import SyncAPIResource, AsyncAPIResource
from .role_bindings import (
    RoleBindingsResource,
    AsyncRoleBindingsResource,
    RoleBindingsResourceWithRawResponse,
    AsyncRoleBindingsResourceWithRawResponse,
    RoleBindingsResourceWithStreamingResponse,
    AsyncRoleBindingsResourceWithStreamingResponse,
)

__all__ = ["IamResource", "AsyncIamResource"]


class IamResource(SyncAPIResource):
    @cached_property
    def role_bindings(self) -> RoleBindingsResource:
        return RoleBindingsResource(self._client)

    @cached_property
    def with_raw_response(self) -> IamResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return IamResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IamResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return IamResourceWithStreamingResponse(self)


class AsyncIamResource(AsyncAPIResource):
    @cached_property
    def role_bindings(self) -> AsyncRoleBindingsResource:
        return AsyncRoleBindingsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncIamResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncIamResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIamResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncIamResourceWithStreamingResponse(self)


class IamResourceWithRawResponse:
    def __init__(self, iam: IamResource) -> None:
        self._iam = iam

    @cached_property
    def role_bindings(self) -> RoleBindingsResourceWithRawResponse:
        return RoleBindingsResourceWithRawResponse(self._iam.role_bindings)


class AsyncIamResourceWithRawResponse:
    def __init__(self, iam: AsyncIamResource) -> None:
        self._iam = iam

    @cached_property
    def role_bindings(self) -> AsyncRoleBindingsResourceWithRawResponse:
        return AsyncRoleBindingsResourceWithRawResponse(self._iam.role_bindings)


class IamResourceWithStreamingResponse:
    def __init__(self, iam: IamResource) -> None:
        self._iam = iam

    @cached_property
    def role_bindings(self) -> RoleBindingsResourceWithStreamingResponse:
        return RoleBindingsResourceWithStreamingResponse(self._iam.role_bindings)


class AsyncIamResourceWithStreamingResponse:
    def __init__(self, iam: AsyncIamResource) -> None:
        self._iam = iam

    @cached_property
    def role_bindings(self) -> AsyncRoleBindingsResourceWithStreamingResponse:
        return AsyncRoleBindingsResourceWithStreamingResponse(self._iam.role_bindings)
