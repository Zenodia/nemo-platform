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
from ...types.iam import (
    role_binding_list_params,
    role_binding_create_params,
    role_binding_delete_params,
)
from ...pagination import SyncDefaultPagination, AsyncDefaultPagination
from ..._base_client import AsyncPaginator, make_request_options
from ...types.iam.role_binding import RoleBinding
from ...types.shared.delete_response import DeleteResponse
from ...types.iam.role_binding_filter_param import RoleBindingFilterParam

__all__ = ["RoleBindingsResource", "AsyncRoleBindingsResource"]


class RoleBindingsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RoleBindingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return RoleBindingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RoleBindingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return RoleBindingsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        principal: str,
        role: str,
        wait_role_propagation: bool | Omit = omit,
        workspace: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleBinding:
        """
        Create a new role binding (Platform Admin only)

        Args:
          principal: The principal identifier (email, user ID, or group ID)

          role: The role name (e.g., 'Viewer', 'Editor', 'Admin')

          wait_role_propagation: If true, wait for role to propagate before returning (default: true). Set to
              false for bulk operations.

          workspace: The workspace this binding applies to. None for platform-level roles.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/apis/auth/v2/iam/role-bindings",
            body=maybe_transform(
                {
                    "principal": principal,
                    "role": role,
                    "workspace": workspace,
                },
                role_binding_create_params.RoleBindingCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"wait_role_propagation": wait_role_propagation}, role_binding_create_params.RoleBindingCreateParams
                ),
            ),
            cast_to=RoleBinding,
        )

    def retrieve(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleBinding:
        """
        Get a specific role binding (Platform Admin only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._get(
            path_template("/apis/auth/v2/iam/role-bindings/{name}", name=name),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleBinding,
        )

    def list(
        self,
        *,
        filter: RoleBindingFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncDefaultPagination[RoleBinding]:
        """
        List all role bindings (Platform Admin only)

        Args:
          filter: Filter role bindings by principal, workspace, role, granted_by, is_active,
              granted_at, and revoked_at.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/apis/auth/v2/iam/role-bindings",
            page=SyncDefaultPagination[RoleBinding],
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
                    role_binding_list_params.RoleBindingListParams,
                ),
            ),
            model=RoleBinding,
        )

    def delete(
        self,
        name: str,
        *,
        wait_role_propagation: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeleteResponse:
        """
        Revoke a role binding (Platform Admin only)

        Args:
          wait_role_propagation: If true, wait for role to propagate before returning (default: true). Set to
              false for bulk operations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._delete(
            path_template("/apis/auth/v2/iam/role-bindings/{name}", name=name),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"wait_role_propagation": wait_role_propagation}, role_binding_delete_params.RoleBindingDeleteParams
                ),
            ),
            cast_to=DeleteResponse,
        )


class AsyncRoleBindingsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRoleBindingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncRoleBindingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRoleBindingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncRoleBindingsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        principal: str,
        role: str,
        wait_role_propagation: bool | Omit = omit,
        workspace: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleBinding:
        """
        Create a new role binding (Platform Admin only)

        Args:
          principal: The principal identifier (email, user ID, or group ID)

          role: The role name (e.g., 'Viewer', 'Editor', 'Admin')

          wait_role_propagation: If true, wait for role to propagate before returning (default: true). Set to
              false for bulk operations.

          workspace: The workspace this binding applies to. None for platform-level roles.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/apis/auth/v2/iam/role-bindings",
            body=await async_maybe_transform(
                {
                    "principal": principal,
                    "role": role,
                    "workspace": workspace,
                },
                role_binding_create_params.RoleBindingCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"wait_role_propagation": wait_role_propagation}, role_binding_create_params.RoleBindingCreateParams
                ),
            ),
            cast_to=RoleBinding,
        )

    async def retrieve(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleBinding:
        """
        Get a specific role binding (Platform Admin only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._get(
            path_template("/apis/auth/v2/iam/role-bindings/{name}", name=name),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleBinding,
        )

    def list(
        self,
        *,
        filter: RoleBindingFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[RoleBinding, AsyncDefaultPagination[RoleBinding]]:
        """
        List all role bindings (Platform Admin only)

        Args:
          filter: Filter role bindings by principal, workspace, role, granted_by, is_active,
              granted_at, and revoked_at.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/apis/auth/v2/iam/role-bindings",
            page=AsyncDefaultPagination[RoleBinding],
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
                    role_binding_list_params.RoleBindingListParams,
                ),
            ),
            model=RoleBinding,
        )

    async def delete(
        self,
        name: str,
        *,
        wait_role_propagation: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeleteResponse:
        """
        Revoke a role binding (Platform Admin only)

        Args:
          wait_role_propagation: If true, wait for role to propagate before returning (default: true). Set to
              false for bulk operations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._delete(
            path_template("/apis/auth/v2/iam/role-bindings/{name}", name=name),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"wait_role_propagation": wait_role_propagation}, role_binding_delete_params.RoleBindingDeleteParams
                ),
            ),
            cast_to=DeleteResponse,
        )


class RoleBindingsResourceWithRawResponse:
    def __init__(self, role_bindings: RoleBindingsResource) -> None:
        self._role_bindings = role_bindings

        self.create = to_raw_response_wrapper(
            role_bindings.create,
        )
        self.retrieve = to_raw_response_wrapper(
            role_bindings.retrieve,
        )
        self.list = to_raw_response_wrapper(
            role_bindings.list,
        )
        self.delete = to_raw_response_wrapper(
            role_bindings.delete,
        )


class AsyncRoleBindingsResourceWithRawResponse:
    def __init__(self, role_bindings: AsyncRoleBindingsResource) -> None:
        self._role_bindings = role_bindings

        self.create = async_to_raw_response_wrapper(
            role_bindings.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            role_bindings.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            role_bindings.list,
        )
        self.delete = async_to_raw_response_wrapper(
            role_bindings.delete,
        )


class RoleBindingsResourceWithStreamingResponse:
    def __init__(self, role_bindings: RoleBindingsResource) -> None:
        self._role_bindings = role_bindings

        self.create = to_streamed_response_wrapper(
            role_bindings.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            role_bindings.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            role_bindings.list,
        )
        self.delete = to_streamed_response_wrapper(
            role_bindings.delete,
        )


class AsyncRoleBindingsResourceWithStreamingResponse:
    def __init__(self, role_bindings: AsyncRoleBindingsResource) -> None:
        self._role_bindings = role_bindings

        self.create = async_to_streamed_response_wrapper(
            role_bindings.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            role_bindings.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            role_bindings.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            role_bindings.delete,
        )
