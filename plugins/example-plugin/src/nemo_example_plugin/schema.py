# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Example API schema definitions — request bodies and filters.

This module contains only API-layer Pydantic models.  Entity definitions
(classes stored in the entity store) live in
:mod:`nemo_example_plugin.entities` — keep the two concerns separate.

Naming conventions:
- ``CreateXRequest`` / ``UpdateXRequest`` — plain :class:`~pydantic.BaseModel`
  for request bodies.  No shared base class is used; all fields are explicit.
- ``XFilter`` — extends :class:`~nemo_platform_plugin.schema.NemoFilter` to inherit
  ``extra="forbid"``, which turns filter field typos into 422 errors instead
  of silently returning unfiltered results.

Entity objects (subclasses of :class:`~nemo_platform_plugin.entity.NemoEntity`) are
returned directly from route handlers as the API response — no separate
response model is needed.  Use ``NemoListResponse[ExampleItem]`` for list
endpoints.
"""

from __future__ import annotations

from nemo_example_plugin.entities import ExampleItem
from nemo_platform_plugin.schema import NemoFilter, NemoListResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Request bodies — plain Pydantic BaseModel, no shared base
# ---------------------------------------------------------------------------


class CreateExampleItemRequest(BaseModel):
    """Request body for ``POST /v2/workspaces/{workspace}/items``."""

    name: str = Field(description="Unique item name within the workspace.")
    title: str = Field(description="Short title for the item.")
    body: str = Field(default="", description="Long-form body text.")
    tags: list[str] = Field(default_factory=list, description="Searchable tags.")


class UpdateExampleItemRequest(BaseModel):
    """Request body for ``PATCH /v2/workspaces/{workspace}/items/{name}``.

    All fields are optional — omitted fields are left unchanged.
    """

    title: str | None = Field(default=None, description="Updated title.")
    body: str | None = Field(default=None, description="Updated body text.")
    tags: list[str] | None = Field(default=None, description="Replacement tag list.")


# ---------------------------------------------------------------------------
# Filter — extends NemoFilter so extra fields are rejected (extra="forbid")
# ---------------------------------------------------------------------------


class ExampleItemFilter(NemoFilter):
    """Query filter for ``GET /v2/workspaces/{workspace}/items``.

    ``extra="forbid"`` is inherited from :class:`~nemo_platform_plugin.schema.NemoFilter`.
    A typo like ``?filter[ttle]=foo`` returns a 422 instead of silently
    returning unfiltered results.

    Usage (deepObject query params)::

        GET /items?filter[title]=hello
        GET /items?filter[tag]=ml
    """

    title: str | None = Field(
        default=None,
        description="Filter to items whose title matches this string.",
    )
    tag: str | None = Field(
        default=None,
        description="Filter to items that have this tag.",
    )


# ---------------------------------------------------------------------------
# List response — entity used directly as item type
# ---------------------------------------------------------------------------

#: Paginated list of :class:`~nemo_example_plugin.entities.ExampleItem` objects.
#: Use as ``response_model=ExampleItemPage`` on list endpoints.
ExampleItemPage = NemoListResponse[ExampleItem]
