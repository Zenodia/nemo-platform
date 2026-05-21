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

from typing import Dict, Iterable

import httpx

from .events import (
    EventsResource,
    AsyncEventsResource,
    EventsResourceWithRawResponse,
    AsyncEventsResourceWithRawResponse,
    EventsResourceWithStreamingResponse,
    AsyncEventsResourceWithStreamingResponse,
)
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
from ....pagination import SyncDefaultPagination, AsyncDefaultPagination
from ...._base_client import AsyncPaginator, make_request_options
from ....types.intake import (
    EntryDataParam,
    EntrySortField,
    entry_list_params,
    entry_patch_params,
    entry_create_params,
)
from ....types.intake.entry import Entry
from ....types.intake.usage_param import UsageParam
from ....types.intake.entry_data_param import EntryDataParam
from ....types.intake.entry_sort_field import EntrySortField
from ....types.intake.user_rating_param import UserRatingParam
from ....types.intake.entry_filter_param import EntryFilterParam
from ....types.intake.entry_context_param import EntryContextParam

__all__ = ["EntriesResource", "AsyncEntriesResource"]


class EntriesResource(SyncAPIResource):
    @cached_property
    def events(self) -> EventsResource:
        return EventsResource(self._client)

    @cached_property
    def with_raw_response(self) -> EntriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return EntriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EntriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return EntriesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        workspace: str | None = None,
        context: EntryContextParam,
        data: EntryDataParam,
        custom_fields: Dict[str, object] | Omit = omit,
        events: Iterable[entry_create_params.Event] | Omit = omit,
        external_id: str | Omit = omit,
        project: str | Omit = omit,
        usage: UsageParam | Omit = omit,
        user_rating: UserRatingParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Entry:
        """
        Create a new entry.

        Apps and tasks referenced in the entry context will be auto-created if they
        don't exist.

        Args:
          context: Contextual metadata attached to every entry record.

              Keeping these grouped in a dedicated object avoids polluting the top-level
              entity schema and makes it trivial to extend without breaking compatibility.

          data: Entry data containing the request and response for an LLM interaction.

          custom_fields: Free-form metadata bag for client-defined fields (e.g., external experiment
              metadata).

          events: Events associated with this entry

          external_id: Optional client-provided identifier (e.g., completion_id from an LLM provider)

          project: The name of the project associated with this entry

          usage: Structured usage metrics captured at log time.

              Every field is optional so producers can populate whatever they have without
              schema breakage. Stored as the entry-level `usage` field so filters can reach it
              via `data.usage.<field>` entity-store paths.

          user_rating: User's rating/evaluation of an AI response.

              This captures various forms of end-user feedback about a model's response,
              including binary thumbs up/down ratings, numeric scores, free-text opinions,
              suggested rewrites, and structured category ratings.

              Either `thumb` or `rating` should be provided (they are mutually exclusive), but
              all fields are optional to accommodate different feedback collection patterns.

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
            path_template("/apis/intake/v2/workspaces/{workspace}/entries", workspace=workspace),
            body=maybe_transform(
                {
                    "context": context,
                    "data": data,
                    "custom_fields": custom_fields,
                    "events": events,
                    "external_id": external_id,
                    "project": project,
                    "usage": usage,
                    "user_rating": user_rating,
                },
                entry_create_params.EntryCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
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
    ) -> Entry:
        """
        Get a specific entry by ID or external_id.

        Use `external:{external_id}` to get by external_id. Example:
        `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`

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
            path_template("/apis/intake/v2/workspaces/{workspace}/entries/{name}", workspace=workspace, name=name),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
        )

    def list(
        self,
        *,
        workspace: str | None = None,
        filter: EntryFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: EntrySortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncDefaultPagination[Entry]:
        """
        List all entries with filtering capabilities.

        When longest_per_thread=true is set in filters, returns only the longest entry
        (by message count) for each unique thread_id.

        Args:
          filter: Filter entries by id, project, external_id, created_at, updated_at, usage fields
              (model), context fields, and user_rating fields.

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
            path_template("/apis/intake/v2/workspaces/{workspace}/entries", workspace=workspace),
            page=SyncDefaultPagination[Entry],
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
                    entry_list_params.EntryListParams,
                ),
            ),
            model=Entry,
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
        Delete an entry by ID or external_id.

        Use `external:{external_id}` to delete by external_id. Example:
        `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`

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
            path_template("/apis/intake/v2/workspaces/{workspace}/entries/{name}", workspace=workspace, name=name),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def patch(
        self,
        name: str,
        *,
        workspace: str | None = None,
        context: EntryContextParam | Omit = omit,
        custom_fields: Dict[str, object] | Omit = omit,
        data: EntryDataParam | Omit = omit,
        events: Iterable[entry_patch_params.Event] | Omit = omit,
        usage: UsageParam | Omit = omit,
        user_rating: UserRatingParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Entry:
        """
        Update an existing entry by ID or external_id.

        Use `external:{external_id}` to update by external_id. Example:
        `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`

        Args:
          context: Contextual metadata attached to every entry record.

              Keeping these grouped in a dedicated object avoids polluting the top-level
              entity schema and makes it trivial to extend without breaking compatibility.

          custom_fields: Free-form metadata bag for client-defined fields (replaces existing value when
              provided).

          data: Entry data containing the request and response for an LLM interaction.

          events: Events associated with this entry

          usage: Structured usage metrics captured at log time.

              Every field is optional so producers can populate whatever they have without
              schema breakage. Stored as the entry-level `usage` field so filters can reach it
              via `data.usage.<field>` entity-store paths.

          user_rating: User's rating/evaluation of an AI response.

              This captures various forms of end-user feedback about a model's response,
              including binary thumbs up/down ratings, numeric scores, free-text opinions,
              suggested rewrites, and structured category ratings.

              Either `thumb` or `rating` should be provided (they are mutually exclusive), but
              all fields are optional to accommodate different feedback collection patterns.

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
        return self._patch(
            path_template("/apis/intake/v2/workspaces/{workspace}/entries/{name}", workspace=workspace, name=name),
            body=maybe_transform(
                {
                    "context": context,
                    "custom_fields": custom_fields,
                    "data": data,
                    "events": events,
                    "usage": usage,
                    "user_rating": user_rating,
                },
                entry_patch_params.EntryPatchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
        )


class AsyncEntriesResource(AsyncAPIResource):
    @cached_property
    def events(self) -> AsyncEventsResource:
        return AsyncEventsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEntriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncEntriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEntriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncEntriesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        workspace: str | None = None,
        context: EntryContextParam,
        data: EntryDataParam,
        custom_fields: Dict[str, object] | Omit = omit,
        events: Iterable[entry_create_params.Event] | Omit = omit,
        external_id: str | Omit = omit,
        project: str | Omit = omit,
        usage: UsageParam | Omit = omit,
        user_rating: UserRatingParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Entry:
        """
        Create a new entry.

        Apps and tasks referenced in the entry context will be auto-created if they
        don't exist.

        Args:
          context: Contextual metadata attached to every entry record.

              Keeping these grouped in a dedicated object avoids polluting the top-level
              entity schema and makes it trivial to extend without breaking compatibility.

          data: Entry data containing the request and response for an LLM interaction.

          custom_fields: Free-form metadata bag for client-defined fields (e.g., external experiment
              metadata).

          events: Events associated with this entry

          external_id: Optional client-provided identifier (e.g., completion_id from an LLM provider)

          project: The name of the project associated with this entry

          usage: Structured usage metrics captured at log time.

              Every field is optional so producers can populate whatever they have without
              schema breakage. Stored as the entry-level `usage` field so filters can reach it
              via `data.usage.<field>` entity-store paths.

          user_rating: User's rating/evaluation of an AI response.

              This captures various forms of end-user feedback about a model's response,
              including binary thumbs up/down ratings, numeric scores, free-text opinions,
              suggested rewrites, and structured category ratings.

              Either `thumb` or `rating` should be provided (they are mutually exclusive), but
              all fields are optional to accommodate different feedback collection patterns.

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
            path_template("/apis/intake/v2/workspaces/{workspace}/entries", workspace=workspace),
            body=await async_maybe_transform(
                {
                    "context": context,
                    "data": data,
                    "custom_fields": custom_fields,
                    "events": events,
                    "external_id": external_id,
                    "project": project,
                    "usage": usage,
                    "user_rating": user_rating,
                },
                entry_create_params.EntryCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
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
    ) -> Entry:
        """
        Get a specific entry by ID or external_id.

        Use `external:{external_id}` to get by external_id. Example:
        `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`

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
            path_template("/apis/intake/v2/workspaces/{workspace}/entries/{name}", workspace=workspace, name=name),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
        )

    def list(
        self,
        *,
        workspace: str | None = None,
        filter: EntryFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: EntrySortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Entry, AsyncDefaultPagination[Entry]]:
        """
        List all entries with filtering capabilities.

        When longest_per_thread=true is set in filters, returns only the longest entry
        (by message count) for each unique thread_id.

        Args:
          filter: Filter entries by id, project, external_id, created_at, updated_at, usage fields
              (model), context fields, and user_rating fields.

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
            path_template("/apis/intake/v2/workspaces/{workspace}/entries", workspace=workspace),
            page=AsyncDefaultPagination[Entry],
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
                    entry_list_params.EntryListParams,
                ),
            ),
            model=Entry,
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
        Delete an entry by ID or external_id.

        Use `external:{external_id}` to delete by external_id. Example:
        `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`

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
            path_template("/apis/intake/v2/workspaces/{workspace}/entries/{name}", workspace=workspace, name=name),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def patch(
        self,
        name: str,
        *,
        workspace: str | None = None,
        context: EntryContextParam | Omit = omit,
        custom_fields: Dict[str, object] | Omit = omit,
        data: EntryDataParam | Omit = omit,
        events: Iterable[entry_patch_params.Event] | Omit = omit,
        usage: UsageParam | Omit = omit,
        user_rating: UserRatingParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Entry:
        """
        Update an existing entry by ID or external_id.

        Use `external:{external_id}` to update by external_id. Example:
        `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`

        Args:
          context: Contextual metadata attached to every entry record.

              Keeping these grouped in a dedicated object avoids polluting the top-level
              entity schema and makes it trivial to extend without breaking compatibility.

          custom_fields: Free-form metadata bag for client-defined fields (replaces existing value when
              provided).

          data: Entry data containing the request and response for an LLM interaction.

          events: Events associated with this entry

          usage: Structured usage metrics captured at log time.

              Every field is optional so producers can populate whatever they have without
              schema breakage. Stored as the entry-level `usage` field so filters can reach it
              via `data.usage.<field>` entity-store paths.

          user_rating: User's rating/evaluation of an AI response.

              This captures various forms of end-user feedback about a model's response,
              including binary thumbs up/down ratings, numeric scores, free-text opinions,
              suggested rewrites, and structured category ratings.

              Either `thumb` or `rating` should be provided (they are mutually exclusive), but
              all fields are optional to accommodate different feedback collection patterns.

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
        return await self._patch(
            path_template("/apis/intake/v2/workspaces/{workspace}/entries/{name}", workspace=workspace, name=name),
            body=await async_maybe_transform(
                {
                    "context": context,
                    "custom_fields": custom_fields,
                    "data": data,
                    "events": events,
                    "usage": usage,
                    "user_rating": user_rating,
                },
                entry_patch_params.EntryPatchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
        )


class EntriesResourceWithRawResponse:
    def __init__(self, entries: EntriesResource) -> None:
        self._entries = entries

        self.create = to_raw_response_wrapper(
            entries.create,
        )
        self.retrieve = to_raw_response_wrapper(
            entries.retrieve,
        )
        self.list = to_raw_response_wrapper(
            entries.list,
        )
        self.delete = to_raw_response_wrapper(
            entries.delete,
        )
        self.patch = to_raw_response_wrapper(
            entries.patch,
        )

    @cached_property
    def events(self) -> EventsResourceWithRawResponse:
        return EventsResourceWithRawResponse(self._entries.events)


class AsyncEntriesResourceWithRawResponse:
    def __init__(self, entries: AsyncEntriesResource) -> None:
        self._entries = entries

        self.create = async_to_raw_response_wrapper(
            entries.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            entries.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            entries.list,
        )
        self.delete = async_to_raw_response_wrapper(
            entries.delete,
        )
        self.patch = async_to_raw_response_wrapper(
            entries.patch,
        )

    @cached_property
    def events(self) -> AsyncEventsResourceWithRawResponse:
        return AsyncEventsResourceWithRawResponse(self._entries.events)


class EntriesResourceWithStreamingResponse:
    def __init__(self, entries: EntriesResource) -> None:
        self._entries = entries

        self.create = to_streamed_response_wrapper(
            entries.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            entries.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            entries.list,
        )
        self.delete = to_streamed_response_wrapper(
            entries.delete,
        )
        self.patch = to_streamed_response_wrapper(
            entries.patch,
        )

    @cached_property
    def events(self) -> EventsResourceWithStreamingResponse:
        return EventsResourceWithStreamingResponse(self._entries.events)


class AsyncEntriesResourceWithStreamingResponse:
    def __init__(self, entries: AsyncEntriesResource) -> None:
        self._entries = entries

        self.create = async_to_streamed_response_wrapper(
            entries.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            entries.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            entries.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            entries.delete,
        )
        self.patch = async_to_streamed_response_wrapper(
            entries.patch,
        )

    @cached_property
    def events(self) -> AsyncEventsResourceWithStreamingResponse:
        return AsyncEventsResourceWithStreamingResponse(self._entries.events)
