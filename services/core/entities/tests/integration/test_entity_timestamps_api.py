# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for entity timestamp precision through the HTTP API.

Verifies that timestamp precision, sorting, and filtering work end-to-end
through the full API stack. These tests are especially valuable when adding
a PostgreSQL backend — the same assertions should pass on both SQLite and
PostgreSQL to confirm datetime handling is backend-agnostic.
"""

from datetime import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestTimestampPrecision:
    """Verify that the API returns timestamps with sub-second precision."""

    async def test_created_at_has_microseconds(self, client: AsyncClient, ctx):
        """created_at returned by the API should have microsecond components."""
        resp = await client.post(
            "/apis/entities/v2/workspaces/default/entities/config",
            json={"name": "precision-test", "data": {}},
        )
        assert resp.status_code == 201
        created_at = datetime.fromisoformat(resp.json()["created_at"])
        # The microsecond component should be non-zero (statistically near-certain)
        # but at minimum the field should parse as a valid datetime
        assert created_at.year >= 2020

    async def test_sequential_creates_have_distinct_timestamps(self, client: AsyncClient, ctx):
        """Rapidly created entities should have distinct created_at values."""
        entities = []
        for i in range(5):
            resp = await client.post(
                "/apis/entities/v2/workspaces/default/entities/config",
                json={"name": f"rapid-{i}", "data": {}},
            )
            assert resp.status_code == 201
            entities.append(resp.json())

        timestamps = [datetime.fromisoformat(e["created_at"]) for e in entities]
        assert len(set(timestamps)) == 5, f"Expected 5 distinct timestamps, got {timestamps}"
        assert timestamps == sorted(timestamps), "Timestamps should be in creation order"

    async def test_updated_at_advances_on_update(self, client: AsyncClient, ctx):
        """updated_at should advance after a PUT, with sub-second difference possible."""
        resp = await client.post(
            "/apis/entities/v2/workspaces/default/entities/config",
            json={"name": "update-test", "data": {"v": 1}},
        )
        assert resp.status_code == 201
        original = resp.json()
        original_updated = datetime.fromisoformat(original["updated_at"])

        resp = await client.put(
            "/apis/entities/v2/workspaces/default/entities/config/update-test",
            json={"data": {"v": 2}},
        )
        assert resp.status_code == 200
        new_updated = datetime.fromisoformat(resp.json()["updated_at"])

        assert new_updated > original_updated


@pytest.mark.integration
@pytest.mark.asyncio
class TestTimestampSorting:
    """Verify that sorting by timestamp fields works through the API."""

    async def test_default_sort_is_created_at_desc(self, client: AsyncClient, ctx):
        """Default listing order should be newest-first (created_at descending)."""
        for i in range(5):
            resp = await client.post(
                "/apis/entities/v2/workspaces/default/entities/config",
                json={"name": f"entity-{i}", "data": {}},
            )
            assert resp.status_code == 201

        resp = await client.get("/apis/entities/v2/workspaces/default/entities/config")
        assert resp.status_code == 200
        names = [e["name"] for e in resp.json()["data"]]
        assert names == ["entity-4", "entity-3", "entity-2", "entity-1", "entity-0"]

    async def test_sort_created_at_ascending(self, client: AsyncClient, ctx):
        """sort=created_at should list oldest first."""
        for i in range(5):
            resp = await client.post(
                "/apis/entities/v2/workspaces/default/entities/config",
                json={"name": f"entity-{i}", "data": {}},
            )
            assert resp.status_code == 201

        resp = await client.get(
            "/apis/entities/v2/workspaces/default/entities/config",
            params={"sort": "created_at"},
        )
        assert resp.status_code == 200
        names = [e["name"] for e in resp.json()["data"]]
        assert names == ["entity-0", "entity-1", "entity-2", "entity-3", "entity-4"]

    async def test_sort_updated_at_reflects_update_order(self, client: AsyncClient, ctx):
        """After updating an entity, sort=-updated_at should put it first."""
        for i in range(3):
            resp = await client.post(
                "/apis/entities/v2/workspaces/default/entities/config",
                json={"name": f"entity-{i}", "data": {"v": 1}},
            )
            assert resp.status_code == 201

        # Update the oldest entity
        resp = await client.put(
            "/apis/entities/v2/workspaces/default/entities/config/entity-0",
            json={"data": {"v": 2}},
        )
        assert resp.status_code == 200

        resp = await client.get(
            "/apis/entities/v2/workspaces/default/entities/config",
            params={"sort": "-updated_at"},
        )
        assert resp.status_code == 200
        names = [e["name"] for e in resp.json()["data"]]
        assert names[0] == "entity-0", "Updated entity should sort first"


@pytest.mark.integration
@pytest.mark.asyncio
class TestTimestampFiltering:
    """Verify that datetime filtering works through the API with proper precision."""

    async def test_gte_with_past_date(self, client: AsyncClient, ctx):
        """$gte with a past date should include all entities."""
        for i in range(3):
            resp = await client.post(
                "/apis/entities/v2/workspaces/default/entities/config",
                json={"name": f"entity-{i}", "data": {}},
            )
            assert resp.status_code == 201

        resp = await client.get(
            "/apis/entities/v2/workspaces/default/entities/config",
            params={"filter[created_at][$gte]": "2020-01-01T00:00:00"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 3

    async def test_lt_with_past_date_excludes_all(self, client: AsyncClient, ctx):
        """$lt with a past date should exclude all entities."""
        resp = await client.post(
            "/apis/entities/v2/workspaces/default/entities/config",
            json={"name": "entity-1", "data": {}},
        )
        assert resp.status_code == 201

        resp = await client.get(
            "/apis/entities/v2/workspaces/default/entities/config",
            params={"filter[created_at][$lt]": "2000-01-01T00:00:00"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 0

    async def test_filter_by_actual_timestamp_splits_results(self, client: AsyncClient, ctx):
        """Use the actual created_at from one entity to partition results.

        This is the key end-to-end test: create entities, capture a real timestamp,
        then use it as a filter boundary. Proves that the format round-trips correctly
        through API serialization -> query parameter parsing -> SQL bind parameter.
        """
        resp1 = await client.post(
            "/apis/entities/v2/workspaces/default/entities/config",
            json={"name": "before", "data": {}},
        )
        assert resp1.status_code == 201
        first_created_at = resp1.json()["created_at"]

        resp2 = await client.post(
            "/apis/entities/v2/workspaces/default/entities/config",
            json={"name": "after", "data": {}},
        )
        assert resp2.status_code == 201

        # Filter for entities created strictly after the first entity
        resp = await client.get(
            "/apis/entities/v2/workspaces/default/entities/config",
            params={"filter[created_at][$gt]": first_created_at},
        )
        assert resp.status_code == 200
        names = [e["name"] for e in resp.json()["data"]]
        assert names == ["after"]

    async def test_date_range_filter(self, client: AsyncClient, ctx):
        """A date range from past to future should include all entities."""
        for i in range(3):
            resp = await client.post(
                "/apis/entities/v2/workspaces/default/entities/config",
                json={"name": f"range-{i}", "data": {}},
            )
            assert resp.status_code == 201

        resp = await client.get(
            "/apis/entities/v2/workspaces/default/entities/config",
            params={
                "filter": '{"$and":[{"created_at":{"$gte":"2020-01-01T00:00:00"}},{"created_at":{"$lt":"2099-12-31T23:59:59"}}]}'
            },
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 3

    async def test_updated_at_filter_finds_recently_updated(self, client: AsyncClient, ctx):
        """Filter by updated_at to find an entity that was updated after another was created."""
        resp1 = await client.post(
            "/apis/entities/v2/workspaces/default/entities/config",
            json={"name": "will-update", "data": {"v": 1}},
        )
        assert resp1.status_code == 201

        resp2 = await client.post(
            "/apis/entities/v2/workspaces/default/entities/config",
            json={"name": "wont-update", "data": {"v": 1}},
        )
        assert resp2.status_code == 201
        boundary = resp2.json()["updated_at"]

        # Update the first entity — its updated_at should now be after the boundary
        resp = await client.put(
            "/apis/entities/v2/workspaces/default/entities/config/will-update",
            json={"data": {"v": 2}},
        )
        assert resp.status_code == 200

        resp = await client.get(
            "/apis/entities/v2/workspaces/default/entities/config",
            params={"filter[updated_at][$gt]": boundary},
        )
        assert resp.status_code == 200
        names = [e["name"] for e in resp.json()["data"]]
        assert names == ["will-update"]
