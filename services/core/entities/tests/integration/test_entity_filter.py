# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for entity search functionality."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestEntitySearch:
    """Test entity search functionality with various operators.

    These tests run against both repository backends using the parametrized fixture.
    """

    async def test_search_by_name_eq(self, client: AsyncClient, ctx):
        """Test searching entities by name using $eq."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "llama-model", "data": {"target_id": "llama-2-7b"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "mistral-model", "data": {"target_id": "mistral-7b"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"name":{"$eq":"llama-model"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "llama-model"

    async def test_search_by_name_like(self, client: AsyncClient, ctx):
        """Test searching entities by name using $like."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "llama-7b-config", "data": {"target_id": "llama-2-7b"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "llama-13b-config", "data": {"target_id": "llama-2-13b"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "mistral-config", "data": {"target_id": "mistral-7b"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"name":{"$like":"llama"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "llama-7b-config" in names
        assert "llama-13b-config" in names
        assert "mistral-config" not in names

    async def test_search_by_name_in(self, client: AsyncClient, ctx):
        """Test searching entities by name using $in."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-alpha", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-beta", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-gamma", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"name":{"$in":"config-alpha,config-gamma"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "config-alpha" in names
        assert "config-gamma" in names
        assert "config-beta" not in names

    async def test_search_by_name_nin(self, client: AsyncClient, ctx):
        """Test searching entities by name using $nin."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "keep-this", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "exclude-alpha", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "exclude-beta", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"name":{"$nin":"exclude-alpha,exclude-beta"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "keep-this"

    async def test_search_data_field_eq(self, client: AsyncClient, ctx):
        """Test searching within the data field using $eq."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-a", "data": {"target_id": "llama-2-7b", "priority": 1}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-b", "data": {"target_id": "mistral-7b", "priority": 2}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"data.target_id":{"$eq":"llama-2-7b"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "config-a"

    async def test_search_data_field_eq_null_matches_missing_key(self, client: AsyncClient, ctx):
        """Test that $eq:null matches entities where the JSON key is absent."""
        # Entity with field present and set to a value
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "finetuned-model", "data": {"finetuning_type": "lora"}},
        )
        # Entity with field completely absent from data
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "base-model", "data": {"description": "auto-discovered"}},
        )
        # Entity with field explicitly set to null
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "base-model-explicit-null", "data": {"finetuning_type": None}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"data.finetuning_type":{"$eq":null}}'},
        )

        assert response.status_code == 200
        result = response.json()
        names = {e["name"] for e in result["data"]}
        assert names == {"base-model", "base-model-explicit-null"}

    async def test_search_data_field_eq_null_excludes_string_null(self, client: AsyncClient, ctx):
        """Test that $eq:null does NOT match entities where the field is the string "null"."""
        # Entity with field set to the string "null"
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "string-null-model", "data": {"finetuning_type": "null"}},
        )
        # Entity with field completely absent (should match)
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "missing-key-model", "data": {"description": "no finetuning_type key"}},
        )
        # Entity with field explicitly set to null (should match)
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "explicit-null-model", "data": {"finetuning_type": None}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"data.finetuning_type":{"$eq":null}}'},
        )

        assert response.status_code == 200
        result = response.json()
        names = {e["name"] for e in result["data"]}
        assert "string-null-model" not in names
        assert "missing-key-model" in names
        assert "explicit-null-model" in names

    async def test_search_data_field_like(self, client: AsyncClient, ctx):
        """Test searching within the data field using $like."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-llama-7b", "data": {"description": "Fine-tuning configuration for llama"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-llama-13b", "data": {"description": "Training setup for llama-13b"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-mistral", "data": {"description": "Mistral tuning config"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"data.description":{"$like":"llama"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "config-llama-7b" in names
        assert "config-llama-13b" in names

    async def test_search_data_field_in(self, client: AsyncClient, ctx):
        """Test searching within the data field using $in."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "cfg-small", "data": {"size": "small"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "cfg-medium", "data": {"size": "medium"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "cfg-large", "data": {"size": "large"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"data.size":{"$in":"small,large"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        sizes = [item["data"]["size"] for item in result["data"]]
        assert "small" in sizes
        assert "large" in sizes
        assert "medium" not in sizes

    async def test_search_logical_and(self, client: AsyncClient, ctx):
        """Test searching with $and operator."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "llama-prod", "data": {"env": "production", "target": "llama"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "llama-dev", "data": {"env": "development", "target": "llama"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "mistral-prod", "data": {"env": "production", "target": "mistral"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"$and":[{"data.env":"production"},{"data.target":"llama"}]}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "llama-prod"

    async def test_search_logical_or(self, client: AsyncClient, ctx):
        """Test searching with $or operator."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-alpha", "data": {"status": "active"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-beta", "data": {"status": "pending"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "config-gamma", "data": {"status": "inactive"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"$or":[{"data.status":"active"},{"data.status":"pending"}]}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        statuses = [item["data"]["status"] for item in result["data"]]
        assert "active" in statuses
        assert "pending" in statuses
        assert "inactive" not in statuses

    async def test_search_logical_not(self, client: AsyncClient, ctx):
        """Test searching with $not operator."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "active-config", "data": {"status": "active"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "inactive-config", "data": {"status": "inactive"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"$not":{"data.status":"active"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "inactive-config"

    async def test_search_combined_with_sorting(self, client: AsyncClient, ctx):
        """Test search combined with sorting."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "zebra-config", "data": {"category": "nlp"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "alpha-config", "data": {"category": "nlp"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "beta-config", "data": {"category": "vision"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={
                "filter": '{"data.category":"nlp"}',
                "sort": "name",
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert names == ["alpha-config", "zebra-config"]

    async def test_search_combined_with_pagination(self, client: AsyncClient, ctx):
        """Test search combined with pagination."""
        for i in range(5):
            await client.post(
                "/apis/entities/v2/workspaces/default/entities/customization_config",
                json={"name": f"searchable-{i:02d}", "data": {"searchable": True}},
            )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "other-config", "data": {"searchable": False}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={
                "filter": '{"data.searchable":true}',
                "page": 1,
                "page_size": 2,
                "sort": "name",
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        assert result["pagination"]["total_results"] == 5
        names = [item["name"] for item in result["data"]]
        assert names == ["searchable-00", "searchable-01"]

        # Verify second page
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={
                "filter": '{"data.searchable":true}',
                "page": 2,
                "page_size": 2,
                "sort": "name",
            },
        )
        assert response.status_code == 200
        result = response.json()
        names = [item["name"] for item in result["data"]]
        assert names == ["searchable-02", "searchable-03"]

    async def test_search_bracket_notation(self, client: AsyncClient, ctx):
        """Test search using bracket notation syntax."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "llama-bracket-test", "data": {"target": "llama"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "mistral-bracket-test", "data": {"target": "mistral"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[name][$like]": "llama"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "llama-bracket-test"

    async def test_search_bracket_notation_eq(self, client: AsyncClient, ctx):
        """Test bracket notation with $eq operator."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "exact-match", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "no-match", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[name][$eq]": "exact-match"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "exact-match"

    async def test_search_bracket_notation_implicit_eq(self, client: AsyncClient, ctx):
        """Test bracket notation without operator (implicit $eq)."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "implicit-eq-test", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "other-entity", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[name]": "implicit-eq-test"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "implicit-eq-test"

    async def test_search_bracket_notation_in(self, client: AsyncClient, ctx):
        """Test bracket notation with $in operator."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "bracket-alpha", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "bracket-beta", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "bracket-gamma", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[name][$in]": "bracket-alpha,bracket-gamma"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "bracket-alpha" in names
        assert "bracket-gamma" in names
        assert "bracket-beta" not in names

    async def test_search_bracket_notation_nin(self, client: AsyncClient, ctx):
        """Test bracket notation with $nin operator."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "keep-this-one", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "exclude-this", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "exclude-that", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[name][$nin]": "exclude-this,exclude-that"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "keep-this-one"

    async def test_search_bracket_notation_gt_lt(self, client: AsyncClient, ctx):
        """Test bracket notation with $gt and $lt operators."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "alpha-item", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "beta-item", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "gamma-item", "data": {}},
        )

        # $gt - should exclude alpha-item
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[name][$gt]": "alpha-item"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "beta-item" in names
        assert "gamma-item" in names
        assert "alpha-item" not in names

        # $lt - should exclude gamma-item
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[name][$lt]": "gamma-item"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "alpha-item" in names
        assert "beta-item" in names
        assert "gamma-item" not in names

    async def test_search_bracket_notation_gte_lte(self, client: AsyncClient, ctx):
        """Test bracket notation with $gte and $lte operators."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "aaa-item", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "bbb-item", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "ccc-item", "data": {}},
        )

        # $gte - should include bbb-item and ccc-item
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[name][$gte]": "bbb-item"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "bbb-item" in names
        assert "ccc-item" in names

        # $lte - should include aaa-item and bbb-item
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[name][$lte]": "bbb-item"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "aaa-item" in names
        assert "bbb-item" in names

    async def test_search_bracket_notation_multiple_fields(self, client: AsyncClient, ctx):
        """Test bracket notation with multiple fields (implicit AND)."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "multi-field-match", "data": {"env": "prod", "tier": "premium"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "multi-field-partial", "data": {"env": "prod", "tier": "basic"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "multi-field-none", "data": {"env": "dev", "tier": "premium"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={
                "filter[data.env][$eq]": "prod",
                "filter[data.tier][$eq]": "premium",
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "multi-field-match"

    async def test_search_bracket_notation_data_field(self, client: AsyncClient, ctx):
        """Test bracket notation on nested data fields."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "data-bracket-a", "data": {"category": "nlp", "priority": "high"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "data-bracket-b", "data": {"category": "vision", "priority": "low"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[data.category][$eq]": "nlp"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "data-bracket-a"

    async def test_search_bracket_notation_data_field_like(self, client: AsyncClient, ctx):
        """Test bracket notation with $like on data fields."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "desc-a", "data": {"description": "This is a llama-based model"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "desc-b", "data": {"description": "This is a mistral-based model"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[data.description][$like]": "llama"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "desc-a"

    async def test_search_bracket_notation_or_operator(self, client: AsyncClient, ctx):
        """Test bracket notation with $or logical operator."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "or-test-active", "data": {"status": "active"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "or-test-pending", "data": {"status": "pending"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "or-test-inactive", "data": {"status": "inactive"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[$or]": '[{"data.status":"active"},{"data.status":"pending"}]'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "or-test-active" in names
        assert "or-test-pending" in names
        assert "or-test-inactive" not in names

    async def test_search_bracket_notation_not_operator(self, client: AsyncClient, ctx):
        """Test bracket notation with $not logical operator."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "not-test-keep", "data": {"archived": False}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "not-test-exclude", "data": {"archived": True}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[$not]": '{"data.archived":true}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "not-test-keep"

    async def test_search_bracket_notation_date_field(self, client: AsyncClient, ctx):
        """Test bracket notation on date fields."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "date-bracket-a", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "date-bracket-b", "data": {}},
        )

        # Search for entities created after a past date
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[created_at][$gte]": "2020-01-01T00:00:00"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2

        # Search for entities created before a past date (should find none)
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter[created_at][$lt]": "2000-01-01T00:00:00"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 0

    async def test_search_bracket_notation_combined_with_sort(self, client: AsyncClient, ctx):
        """Test bracket notation combined with sorting."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "zebra-bracket", "data": {"type": "animal"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "apple-bracket", "data": {"type": "fruit"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "banana-bracket", "data": {"type": "fruit"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={
                "filter[data.type][$eq]": "fruit",
                "sort": "name",
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert names == ["apple-bracket", "banana-bracket"]

    async def test_search_bracket_notation_combined_with_pagination(self, client: AsyncClient, ctx):
        """Test bracket notation combined with pagination."""
        for i in range(5):
            await client.post(
                "/apis/entities/v2/workspaces/default/entities/customization_config",
                json={"name": f"paginated-{i:02d}", "data": {"category": "paginated"}},
            )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "not-paginated", "data": {"category": "other"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={
                "filter[data.category][$eq]": "paginated",
                "page": 1,
                "page_size": 2,
                "sort": "name",
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        assert result["pagination"]["total_results"] == 5
        names = [item["name"] for item in result["data"]]
        assert names == ["paginated-00", "paginated-01"]

    async def test_search_multiple_conditions_implicit_and(self, client: AsyncClient, ctx):
        """Test search with multiple conditions (implicit AND)."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "multi-cond-match", "data": {"env": "prod", "region": "us-east"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "multi-cond-partial", "data": {"env": "prod", "region": "eu-west"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "multi-cond-none", "data": {"env": "dev", "region": "us-east"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"data.env":"prod","data.region":"us-east"}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "multi-cond-match"

    async def test_search_nested_logical_operators(self, client: AsyncClient, ctx):
        """Test nested logical operators ($or inside $and)."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "match-a", "data": {"tier": "premium", "region": "us"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "match-b", "data": {"tier": "premium", "region": "eu"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "no-match", "data": {"tier": "basic", "region": "us"}},
        )

        # Find premium tier in either US or EU
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"$and":[{"data.tier":"premium"},{"$or":[{"data.region":"us"},{"data.region":"eu"}]}]}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "match-a" in names
        assert "match-b" in names

    async def test_search_field_level_or(self, client: AsyncClient, ctx):
        """Test $or at field level for multiple possible values."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "status-a", "data": {"status": "completed"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "status-b", "data": {"status": "running"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "status-c", "data": {"status": "failed"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"data.status":{"$or":[{"$eq":"completed"},{"$eq":"failed"}]}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        statuses = [item["data"]["status"] for item in result["data"]]
        assert "completed" in statuses
        assert "failed" in statuses
        assert "running" not in statuses

    async def test_search_with_not_like(self, client: AsyncClient, ctx):
        """Test $not combined with $like operator."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "test-config", "data": {"model": "test-model-v1"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "prod-config", "data": {"model": "production-model"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"name":{"$not":{"$like":"test"}}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "prod-config"

    async def test_search_name_gt(self, client: AsyncClient, ctx):
        """Test $gt operator on name field (lexicographic comparison)."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "alpha-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "beta-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "gamma-config", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"name":{"$gt":"beta-config"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "gamma-config"

    async def test_search_name_gte(self, client: AsyncClient, ctx):
        """Test $gte operator on name field (lexicographic comparison)."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "alpha-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "beta-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "gamma-config", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"name":{"$gte":"beta-config"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "beta-config" in names
        assert "gamma-config" in names
        assert "alpha-config" not in names

    async def test_search_name_lt(self, client: AsyncClient, ctx):
        """Test $lt operator on name field (lexicographic comparison)."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "alpha-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "beta-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "gamma-config", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"name":{"$lt":"beta-config"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "alpha-config"

    async def test_search_name_lte(self, client: AsyncClient, ctx):
        """Test $lte operator on name field (lexicographic comparison)."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "alpha-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "beta-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "gamma-config", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"name":{"$lte":"beta-config"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "alpha-config" in names
        assert "beta-config" in names
        assert "gamma-config" not in names

    async def test_search_name_range(self, client: AsyncClient, ctx):
        """Test range search using $gte and $lt together."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "alpha-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "beta-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "gamma-config", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "delta-config", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"$and":[{"name":{"$gte":"beta-config"}},{"name":{"$lt":"gamma-config"}}]}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "beta-config" in names
        assert "delta-config" in names

    async def test_search_data_field_nin(self, client: AsyncClient, ctx):
        """Test $nin operator on data field."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "keep-me", "data": {"priority": "high"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "exclude-low", "data": {"priority": "low"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "exclude-medium", "data": {"priority": "medium"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"data.priority":{"$nin":"low,medium"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "keep-me"

    async def test_search_boolean_data_field(self, client: AsyncClient, ctx):
        """Test searching for boolean values in data field."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "enabled-config", "data": {"active": True}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "disabled-config", "data": {"active": False}},
        )

        # Search for active=true
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"data.active":true}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "enabled-config"

        # Search for active=false
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"data.active":false}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "disabled-config"

    async def test_search_created_at_gt(self, client: AsyncClient, ctx):
        """Test $gt operator on created_at date field using a past date."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "entity-first", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "entity-second", "data": {}},
        )

        # Search for entities created after a date in the past
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"created_at":{"$gt":"2020-01-01T00:00:00"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "entity-first" in names
        assert "entity-second" in names

    async def test_search_created_at_gte(self, client: AsyncClient, ctx):
        """Test $gte operator on created_at date field."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "entity-alpha", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "entity-beta", "data": {}},
        )

        # Search for entities created at or after a date in the past
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"created_at":{"$gte":"2020-01-01T00:00:00"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "entity-alpha" in names
        assert "entity-beta" in names

    async def test_search_created_at_lt(self, client: AsyncClient, ctx):
        """Test $lt operator on created_at date field."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "old-entity", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "new-entity", "data": {}},
        )

        # Search for entities created before a date in the future (should find all)
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"created_at":{"$lt":"2099-12-31T23:59:59"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "old-entity" in names
        assert "new-entity" in names

        # Search for entities created before a date in the past (should find none)
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"created_at":{"$lt":"2000-01-01T00:00:00"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 0

    async def test_search_created_at_lte(self, client: AsyncClient, ctx):
        """Test $lte operator on created_at date field."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "first-entity", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "second-entity", "data": {}},
        )

        # Search for entities created at or before a date in the future
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"created_at":{"$lte":"2099-12-31T23:59:59"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "first-entity" in names
        assert "second-entity" in names

    async def test_search_created_at_range(self, client: AsyncClient, ctx):
        """Test date range search using $gte and $lt together."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "range-start", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "range-middle", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "range-end", "data": {}},
        )

        # Search for entities within a broad date range
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={
                "filter": '{"$and":[{"created_at":{"$gte":"2020-01-01T00:00:00"}},{"created_at":{"$lt":"2099-12-31T23:59:59"}}]}'
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 3
        names = [item["name"] for item in result["data"]]
        assert "range-start" in names
        assert "range-middle" in names
        assert "range-end" in names

        # Search for entities outside the date range (past only)
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={
                "filter": '{"$and":[{"created_at":{"$gte":"2000-01-01T00:00:00"}},{"created_at":{"$lt":"2010-01-01T00:00:00"}}]}'
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 0

    async def test_search_updated_at_gte(self, client: AsyncClient, ctx):
        """Test $gte operator on updated_at date field."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "will-update", "data": {"version": 1}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "no-update", "data": {"version": 1}},
        )

        # Update the first entity
        await client.put(
            "/apis/entities/v2/workspaces/default/entities/customization_config/will-update",
            json={"data": {"version": 2}},
        )

        # Search for entities updated at or after a date in the past (should find all)
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"updated_at":{"$gte":"2020-01-01T00:00:00"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "will-update" in names
        assert "no-update" in names

    async def test_search_updated_at_lt(self, client: AsyncClient, ctx):
        """Test $lt operator on updated_at date field."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "entity-a", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "entity-b", "data": {}},
        )

        # Search for entities updated before a date in the future
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"updated_at":{"$lt":"2099-12-31T23:59:59"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2

        # Search for entities updated before a date in the past (none expected)
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"updated_at":{"$lt":"2000-01-01T00:00:00"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 0

    async def test_search_with_past_date(self, client: AsyncClient, ctx):
        """Test searching with a date far in the past returns all entities."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "past-test-a", "data": {}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "past-test-b", "data": {}},
        )

        # Search for entities created after a date far in the past
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"created_at":{"$gte":"2020-01-01T00:00:00"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 2
        names = [item["name"] for item in result["data"]]
        assert "past-test-a" in names
        assert "past-test-b" in names

    async def test_search_with_future_date(self, client: AsyncClient, ctx):
        """Test searching with a date in the future returns no entities."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "future-test", "data": {}},
        )

        # Search for entities created after a date in the future
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"created_at":{"$gt":"2099-12-31T23:59:59"}}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 0

    async def test_search_date_combined_with_other_filters(self, client: AsyncClient, ctx):
        """Test combining date filters with other search conditions."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "llama-recent", "data": {"model": "llama"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={"name": "mistral-recent", "data": {"model": "mistral"}},
        )

        # Search for llama models created after a past date
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"$and":[{"data.model":"llama"},{"created_at":{"$gte":"2020-01-01T00:00:00"}}]}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "llama-recent"

        # Search for models created after a future date (should find none)
        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            params={"filter": '{"$and":[{"data.model":"llama"},{"created_at":{"$gt":"2099-12-31T23:59:59"}}]}'},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) == 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestRelationshipSearch:
    """Test relationship-aware search (EXISTS subqueries for parent-child entities)."""

    async def _create_model_with_adapters(
        self,
        client: AsyncClient,
        model_name: str,
        adapter_specs: list[dict],
        model_workspace: str = "default",
    ) -> str:
        """Create a model entity and child adapter entities. Returns model ID.

        Each *adapter_specs* item must include ``name``; optional ``data`` is passed through.
        Optional ``workspace`` selects the workspace for that adapter's POST (defaults to
        *model_workspace*).
        """
        resp = await client.post(
            f"/apis/entities/v2/workspaces/{model_workspace}/entities/model",
            json={"name": model_name, "data": {"description": f"Model {model_name}"}},
        )
        assert resp.status_code == 201
        model_id = resp.json()["id"]

        for spec in adapter_specs:
            adapter_ws = spec.get("workspace", model_workspace)
            resp = await client.post(
                f"/apis/entities/v2/workspaces/{adapter_ws}/entities/adapter",
                json={
                    "name": spec["name"],
                    "parent": model_id,
                    "data": spec.get("data", {}),
                },
            )
            assert resp.status_code == 201

        return model_id

    async def test_exists_true_json(self, client: AsyncClient, ctx):
        """search={"adapters":{"$exists":true}} returns only models with adapters."""
        await self._create_model_with_adapters(client, "model-with-adapter", [{"name": "lora-1", "data": {}}])
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "model-no-adapter", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"adapters":{"$exists":true}}'},
        )
        assert response.status_code == 200
        names = [e["name"] for e in response.json()["data"]]
        assert "model-with-adapter" in names
        assert "model-no-adapter" not in names

    async def test_exists_false_json(self, client: AsyncClient, ctx):
        """search={"adapters":{"$exists":false}} returns only models without adapters."""
        await self._create_model_with_adapters(client, "has-adapter", [{"name": "a1", "data": {}}])
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "no-adapter", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"adapters":{"$exists":false}}'},
        )
        assert response.status_code == 200
        names = [e["name"] for e in response.json()["data"]]
        assert "no-adapter" in names
        assert "has-adapter" not in names

    async def test_child_field_filter_json(self, client: AsyncClient, ctx):
        """search={"adapters":{"finetuning_type":"LoRA"}} filters by child data field."""
        await self._create_model_with_adapters(
            client,
            "lora-model",
            [{"name": "lora-adapter", "data": {"finetuning_type": "LoRA"}}],
        )
        await self._create_model_with_adapters(
            client,
            "ptuning-model",
            [{"name": "pt-adapter", "data": {"finetuning_type": "P_TUNING"}}],
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "bare-model", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"adapters":{"finetuning_type":"LoRA"}}'},
        )
        assert response.status_code == 200
        names = [e["name"] for e in response.json()["data"]]
        assert names == ["lora-model"]

    async def test_exists_bracket_notation(self, client: AsyncClient, ctx):
        """filter[adapters][$exists]=true via bracket notation."""
        await self._create_model_with_adapters(client, "has-child", [{"name": "c1", "data": {}}])
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "no-child", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter[adapters][$exists]": "true"},
        )
        assert response.status_code == 200
        names = [e["name"] for e in response.json()["data"]]
        assert "has-child" in names
        assert "no-child" not in names

    async def test_child_field_bracket_notation(self, client: AsyncClient, ctx):
        """filter[adapters][finetuning_type]=LoRA via bracket notation."""
        await self._create_model_with_adapters(
            client,
            "bracket-lora",
            [{"name": "adapter-l", "data": {"finetuning_type": "LoRA"}}],
        )
        await self._create_model_with_adapters(
            client,
            "bracket-pt",
            [{"name": "adapter-p", "data": {"finetuning_type": "P_TUNING"}}],
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter[adapters][finetuning_type]": "LoRA"},
        )
        assert response.status_code == 200
        names = [e["name"] for e in response.json()["data"]]
        assert names == ["bracket-lora"]

    async def test_child_field_with_operator_bracket(self, client: AsyncClient, ctx):
        """filter[adapters][finetuning_type][$in]=LoRA,P_TUNING via bracket notation."""
        await self._create_model_with_adapters(
            client,
            "m-lora",
            [{"name": "a-lora", "data": {"finetuning_type": "LoRA"}}],
        )
        await self._create_model_with_adapters(
            client,
            "m-pt",
            [{"name": "a-pt", "data": {"finetuning_type": "P_TUNING"}}],
        )
        await self._create_model_with_adapters(
            client,
            "m-other",
            [{"name": "a-other", "data": {"finetuning_type": "FULL"}}],
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter[adapters][finetuning_type][$in]": "LoRA,P_TUNING"},
        )
        assert response.status_code == 200
        names = sorted(e["name"] for e in response.json()["data"])
        assert names == ["m-lora", "m-pt"]

    async def test_combined_relationship_and_field_filter(self, client: AsyncClient, ctx):
        """Combine relationship filter with direct field filter."""
        await self._create_model_with_adapters(
            client,
            "llama-with-lora",
            [{"name": "lora-a", "data": {"finetuning_type": "LoRA"}}],
        )
        await self._create_model_with_adapters(
            client,
            "mistral-with-lora",
            [{"name": "lora-b", "data": {"finetuning_type": "LoRA"}}],
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={
                "filter[name][$like]": "llama",
                "filter[adapters][finetuning_type]": "LoRA",
            },
        )
        assert response.status_code == 200
        names = [e["name"] for e in response.json()["data"]]
        assert names == ["llama-with-lora"]

    async def test_pagination_with_relationship_filter(self, client: AsyncClient, ctx):
        """Pagination works correctly with relationship filters."""
        for i in range(5):
            await self._create_model_with_adapters(
                client,
                f"paginated-model-{i:02d}",
                [{"name": f"adapter-{i}", "data": {"finetuning_type": "LoRA"}}],
            )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "no-adapter-model", "data": {}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={
                "filter": '{"adapters":{"$exists":true}}',
                "page": 1,
                "page_size": 2,
                "sort": "name",
            },
        )
        assert response.status_code == 200
        result = response.json()
        assert result["pagination"]["total_results"] == 5
        assert len(result["data"]) == 2
        names = [e["name"] for e in result["data"]]
        assert names == ["paginated-model-00", "paginated-model-01"]

    async def test_relationship_filter_after_adapter_moved_to_different_workspace(self, client: AsyncClient, ctx):
        """Model/adapters search stays correct when a child is created in a new workspace
        (delete + recreate) or created directly in another workspace.
        The EXISTS subquery must join on parent only, not child workspace.
        """
        other_ws = "other-ws"
        wresp = await client.post(
            "/apis/entities/v2/workspaces",
            json={"name": other_ws, "description": "Second workspace for adapter moves"},
        )
        assert wresp.status_code == 201

        model_id = await self._create_model_with_adapters(
            client,
            "moved-adapter-model",
            [{"name": "movable-adapter", "data": {"finetuning_type": "LoRA"}}],
        )
        assert model_id  # id returned for the delete+recreate path below

        async def assert_filters_find_model() -> None:
            """Re-run EXISTS and finetuning_type filters; the moved-adapter model must still match both."""
            r1 = await client.get(
                "/apis/entities/v2/workspaces/default/entities/model",
                params={"filter": '{"adapters":{"$exists":true}}'},
            )
            assert r1.status_code == 200
            n1 = [e["name"] for e in r1.json()["data"]]
            assert "moved-adapter-model" in n1

            r2 = await client.get(
                "/apis/entities/v2/workspaces/default/entities/model",
                params={"filter": '{"adapters":{"finetuning_type":"LoRA"}}'},
            )
            assert r2.status_code == 200
            n2 = [e["name"] for e in r2.json()["data"]]
            assert n2 == ["moved-adapter-model"]

        await assert_filters_find_model()

        dresp = await client.delete(
            f"/apis/entities/v2/workspaces/default/entities/adapter/movable-adapter?parent={model_id}",
        )
        assert dresp.status_code == 200

        cresp = await client.post(
            f"/apis/entities/v2/workspaces/{other_ws}/entities/adapter",
            json={
                "name": "movable-adapter",
                "parent": model_id,
                "data": {"finetuning_type": "LoRA"},
            },
        )
        assert cresp.status_code == 201
        assert cresp.json()["workspace"] == other_ws

        await assert_filters_find_model()

        # Adapter created in other workspace from the start (no delete step)
        await self._create_model_with_adapters(
            client,
            "native-cross-ws-model",
            [
                {
                    "name": "child-in-other",
                    "data": {"finetuning_type": "P_TUNING"},
                    "workspace": other_ws,
                },
            ],
        )
        r3 = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"adapters":{"$exists":true}}'},
        )
        assert r3.status_code == 200
        names3 = {e["name"] for e in r3.json()["data"]}
        assert "native-cross-ws-model" in names3

    async def test_batch_fetch_children_and_group_by_parent(self, client: AsyncClient, ctx):
        """Simulate the two-request pattern for fetching models + their adapters.

        1. GET models with adapters (relationship filter)
        2. GET all adapters for those models in one batch (search[parent][$in]=...)
        3. Group adapters by parent client-side
        """
        # Setup: 3 models, 2 with adapters of varying types
        m1_id = await self._create_model_with_adapters(
            client,
            "llama-7b",
            [
                {"name": "lora-a", "data": {"finetuning_type": "LoRA"}},
                {"name": "lora-b", "data": {"finetuning_type": "LoRA"}},
            ],
        )
        m2_id = await self._create_model_with_adapters(
            client,
            "mistral-7b",
            [
                {"name": "pt-adapter", "data": {"finetuning_type": "P_TUNING"}},
            ],
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "bare-model", "data": {}},
        )

        # Request 1: get models that have adapters
        resp1 = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter[adapters][$exists]": "true"},
        )
        assert resp1.status_code == 200
        models = resp1.json()["data"]
        assert len(models) == 2
        model_ids = [m["id"] for m in models]
        assert set(model_ids) == {m1_id, m2_id}

        # Request 2: batch-fetch all adapters for those models
        resp2 = await client.get(
            "/apis/entities/v2/workspaces/default/entities/adapter",
            params={"filter[parent][$in]": ",".join(model_ids)},
        )
        assert resp2.status_code == 200
        adapters = resp2.json()["data"]
        assert len(adapters) == 3

        # Group by parent client-side
        from collections import defaultdict

        grouped: dict[str, list[str]] = defaultdict(list)
        for adapter in adapters:
            assert adapter["parent"] is not None, "parent must be visible in response"
            grouped[adapter["parent"]].append(adapter["name"])

        assert sorted(grouped[m1_id]) == ["lora-a", "lora-b"]
        assert grouped[m2_id] == ["pt-adapter"]


@pytest.mark.integration
@pytest.mark.asyncio
class TestNullFieldSearch:
    """Test $eq:null and $not:$eq:null on data fields that may be null or absent.

    This is the core bug from issue #3976: the entity store's $eq:null
    operator must correctly match fields that are either explicitly null
    in the JSON or completely absent from the data dict.

    In production, models created through the Models API always store
    finetuning_type and prompt as explicit null (via Pydantic model_dump
    without exclude_none). But entities created by other code paths or
    older migrations may have these fields entirely absent. Both cases
    must be handled.
    """

    async def _seed_entities(self, client: AsyncClient):
        """Create entities representing the real-world data shapes we need to filter.

        Covers four distinct states a nullable field can be in:
        1. Absent     — field not present in the data dict at all
        2. Explicit null — field present with value null
        3. Non-null value — field present with a meaningful value
        4. Empty array — field present but empty (e.g. adapters: [])
        """
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={
                "name": "nim-field-absent",
                "data": {
                    "description": "Simulates an entity where finetuning_type and prompt are not stored at all",
                },
            },
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={
                "name": "nim-explicit-null",
                "data": {
                    "description": "Simulates a model created via the API — finetuning_type and prompt are null via Pydantic defaults",
                    "finetuning_type": None,
                    "prompt": None,
                    "adapters": [],
                },
            },
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={
                "name": "nim-finetuned",
                "data": {
                    "description": "Fine-tuned model with a non-null finetuning_type",
                    "finetuning_type": "sft",
                    "prompt": None,
                    "adapters": [],
                },
            },
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={
                "name": "nim-prompt-configured",
                "data": {
                    "description": "Prompt-configured model with a non-null prompt object",
                    "finetuning_type": None,
                    "prompt": {"template": "You are a helpful assistant."},
                    "adapters": [],
                },
            },
        )

    # -- finetuning_type tests --

    async def test_eq_null_matches_absent_and_explicit_null_finetuning_type(self, client: AsyncClient, ctx):
        """$eq:null should match entities where finetuning_type is absent OR explicitly null."""
        await self._seed_entities(client)

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"data.finetuning_type":{"$eq":null}}'},
        )

        assert response.status_code == 200
        names = sorted(item["name"] for item in response.json()["data"])
        assert "nim-field-absent" in names, "absent field should match $eq:null"
        assert "nim-explicit-null" in names, "explicit null should match $eq:null"
        assert "nim-prompt-configured" in names, "null finetuning_type should match $eq:null"
        assert "nim-finetuned" not in names, "non-null finetuning_type should NOT match $eq:null"

    async def test_not_eq_null_matches_only_present_finetuning_type(self, client: AsyncClient, ctx):
        """$not:$eq:null should match only entities where finetuning_type has a non-null value."""
        await self._seed_entities(client)

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"data.finetuning_type":{"$not":{"$eq":null}}}'},
        )

        assert response.status_code == 200
        names = [item["name"] for item in response.json()["data"]]
        assert names == ["nim-finetuned"], "only the entity with a non-null finetuning_type should match $not:$eq:null"

    # -- prompt tests --

    async def test_eq_null_matches_absent_and_explicit_null_prompt(self, client: AsyncClient, ctx):
        """$eq:null should match entities where prompt is absent OR explicitly null."""
        await self._seed_entities(client)

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"data.prompt":{"$eq":null}}'},
        )

        assert response.status_code == 200
        names = sorted(item["name"] for item in response.json()["data"])
        assert "nim-field-absent" in names, "absent field should match $eq:null"
        assert "nim-explicit-null" in names, "explicit null should match $eq:null"
        assert "nim-finetuned" in names, "null prompt should match $eq:null"
        assert "nim-prompt-configured" not in names, "non-null prompt should NOT match $eq:null"

    # -- adapters (empty array) tests --

    async def test_eq_null_does_not_match_empty_array(self, client: AsyncClient, ctx):
        """$eq:null should NOT match fields that contain an empty array.

        The adapters field on base NIMs is stored as [] (empty array), which
        is a present, non-null value. $eq:null must not confuse empty arrays
        with null/absent fields.
        """
        await self._seed_entities(client)

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"data.adapters":{"$eq":null}}'},
        )

        assert response.status_code == 200
        names = sorted(item["name"] for item in response.json()["data"])
        # nim-field-absent has no adapters key at all — should match
        assert "nim-field-absent" in names, "absent adapters field should match $eq:null"
        # entities with adapters: [] should NOT match — empty array is not null
        assert "nim-explicit-null" not in names, "adapters: [] should NOT match $eq:null"
        assert "nim-finetuned" not in names, "adapters: [] should NOT match $eq:null"
        assert "nim-prompt-configured" not in names, "adapters: [] should NOT match $eq:null"

    async def test_search_not_null_single_field(self, client: AsyncClient, ctx):
        """Regression: $not:$eq:null must return only entities where the field is present and non-null."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "has-endpoint", "data": {"api_endpoint": "http://localhost:8000"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "no-endpoint", "data": {"description": "no endpoint key"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "null-endpoint", "data": {"api_endpoint": None}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"data.api_endpoint":{"$not":{"$eq":null}}}'},
        )

        assert response.status_code == 200
        names = {e["name"] for e in response.json()["data"]}
        assert "has-endpoint" in names
        assert "no-endpoint" not in names
        assert "null-endpoint" not in names

    async def test_search_not_null_combined_with_other_param(self, client: AsyncClient, ctx):
        """Regression: $not:$eq:null ANDed with another search condition must work end-to-end."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "llama-with-endpoint", "data": {"api_endpoint": "http://llama/v1", "base_model": "llama"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "llama-no-endpoint", "data": {"base_model": "llama"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={
                "name": "mistral-with-endpoint",
                "data": {"api_endpoint": "http://mistral/v1", "base_model": "mistral"},
            },
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={"filter": '{"$and":[{"data.base_model":"llama"},{"data.api_endpoint":{"$not":{"$eq":null}}}]}'},
        )

        assert response.status_code == 200
        names = {e["name"] for e in response.json()["data"]}
        assert names == {"llama-with-endpoint"}

    async def test_search_two_not_nulls_combined(self, client: AsyncClient, ctx):
        """Regression: two $not:$eq:null conditions ANDed together must both be evaluated correctly."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "both-fields", "data": {"api_endpoint": "http://localhost/v1", "prompt": "You are helpful."}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "only-endpoint", "data": {"api_endpoint": "http://localhost/v1"}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "only-prompt", "data": {"prompt": "You are helpful."}},
        )
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/model",
            json={"name": "neither-field", "data": {"description": "plain model"}},
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/model",
            params={
                "filter": '{"$and":[{"data.api_endpoint":{"$not":{"$eq":null}}},{"data.prompt":{"$not":{"$eq":null}}}]}'
            },
        )

        assert response.status_code == 200
        names = {e["name"] for e in response.json()["data"]}
        assert names == {"both-fields"}
