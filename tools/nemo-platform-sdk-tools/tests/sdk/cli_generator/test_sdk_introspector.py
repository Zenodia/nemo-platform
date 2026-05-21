# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest
from nemo_platform_sdk_tools.sdk.cli_generator.sdk_introspector import (
    ParsedDocstring,
    SDKIntrospector,
    introspect_typed_dict,
)


@pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
def test_introspect_datasets_resource():
    """Test introspecting the datasets resource."""
    introspector = SDKIntrospector()
    methods = introspector.introspect_resource(["datasets"])

    # Should have found the standard CRUD methods
    assert "list" in methods
    assert "create" in methods
    assert "retrieve" in methods
    assert "update" in methods
    assert "delete" in methods

    # Check the create method
    create_method = methods["create"]
    assert create_method.name == "create"

    print("\n=== Datasets.create method ===")
    print(f"Parameters ({len(create_method.parameters)}):")
    for param in create_method.parameters:
        print(f"  - {param.name}: {param.python_type_name}")
        print(f"    Required: {param.is_required}, Path param: {param.is_path_param}")
        print(f"    Default: {param.default}")
        print(f"    Dict type: {param.is_dict_type}, List type: {param.is_list_type}")

    # Should have files_url as required
    files_url_params = [p for p in create_method.parameters if p.name == "files_url"]
    assert len(files_url_params) == 1
    files_url_param = files_url_params[0]
    assert files_url_param.is_required
    assert files_url_param.python_type_name == "str"

    # Should have optional parameters
    optional_params = [p for p in create_method.parameters if not p.is_path_param and not p.is_required]
    print(f"\nOptional parameters: {[p.name for p in optional_params]}")
    assert len(optional_params) > 0


@pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
def test_introspect_customization_jobs():
    """Test introspecting customization jobs resource."""
    introspector = SDKIntrospector()
    methods = introspector.introspect_resource(["customization", "jobs"])

    print("\n=== Customization.jobs methods ===")
    print(f"Found methods: {list(methods.keys())}")

    # Should have job-related methods
    assert "list" in methods
    assert "create" in methods
    assert "retrieve" in methods
    assert "cancel" in methods

    # Check the list method
    list_method = methods["list"]
    print("\n=== Customization.jobs.list method ===")
    print(f"Parameters ({len(list_method.parameters)}):")
    for param in list_method.parameters:
        print(f"  - {param.name}: {param.python_type_name}")
        print(f"    Required: {param.is_required}, Default: {param.default}")

    # Should have pagination parameters
    param_names = [p.name for p in list_method.parameters]
    assert "page" in param_names
    assert "page_size" in param_names


@pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
def test_introspect_namespaces():
    """Test introspecting namespaces resource."""
    introspector = SDKIntrospector()
    methods = introspector.introspect_resource(["namespaces"])

    print("\n=== Namespaces methods ===")
    print(f"Found methods: {list(methods.keys())}")

    # Check retrieve method to see path parameters
    retrieve_method = methods["retrieve"]
    print("\n=== Namespaces.retrieve method ===")
    print(f"Parameters ({len(retrieve_method.parameters)}):")
    for param in retrieve_method.parameters:
        print(f"  - {param.name}: {param.python_type_name}")
        print(f"    Required: {param.is_required}, Path param: {param.is_path_param}")
        print(f"    Default: {param.default}")

    # The first parameter should be the ID (path param)
    path_params = retrieve_method.path_parameters
    print(f"\nPath parameters: {[p.name for p in path_params]}")
    assert len(path_params) >= 1


def test_parse_docstring_basic():
    """Test basic docstring parsing."""
    # This matches the format that inspect.getdoc() returns (normalized indentation)
    docstring = (
        "List available customization jobs.\n"
        "\n"
        "Args:\n"
        "  filter: Filter jobs on various criteria.\n"
        "\n"
        "  page: Page number.\n"
        "\n"
        "  page_size: Page size.\n"
        "\n"
        "  sort: The field to sort by. To sort in decreasing order, use `-` in front of the field\n"
        "      name.\n"
        "\n"
        "  extra_headers: Send extra headers\n"
        "\n"
        "  timeout: Override the client-level default timeout for this request, in seconds"
    )
    parsed = ParsedDocstring.parse(docstring)

    assert parsed.description == "List available customization jobs."
    assert parsed.param_descriptions["filter"] == "Filter jobs on various criteria."
    assert parsed.param_descriptions["page"] == "Page number."
    assert parsed.param_descriptions["page_size"] == "Page size."
    assert "The field to sort by" in parsed.param_descriptions["sort"]
    assert "decreasing order" in parsed.param_descriptions["sort"]


def test_parse_docstring_empty():
    """Test parsing empty/None docstrings."""
    parsed = ParsedDocstring.parse(None)
    assert parsed.description == ""
    assert parsed.param_descriptions == {}

    parsed = ParsedDocstring.parse("")
    assert parsed.description == ""
    assert parsed.param_descriptions == {}


def test_parse_docstring_no_args():
    """Test parsing docstring without Args section."""
    docstring = "Get the current user."
    parsed = ParsedDocstring.parse(docstring)
    assert parsed.description == "Get the current user."
    assert parsed.param_descriptions == {}


@pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
def test_sdk_method_docstring_parsing():
    """Test that SDKMethod correctly parses docstrings from SDK."""
    introspector = SDKIntrospector()
    methods = introspector.introspect_resource(["customization", "jobs"])

    list_method = methods["list"]

    # Should have parsed docstring
    assert list_method.description == "List available customization jobs."
    assert list_method.get_param_description("filter") == "Filter jobs on various criteria."
    assert "field to sort by" in (list_method.get_param_description("sort") or "")


class TestTypedDictFieldIsListType:
    """Tests for TypedDictField.is_list_type detection."""

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_search_fields_with_sequence_are_list_types(self):
        """Search fields with Union[str, Sequence[str]] should be detected as list types."""
        from nemo_platform.types.dataset_search_param import DatasetSearchParam

        fields = introspect_typed_dict(DatasetSearchParam)
        field_map = {f.name: f for f in fields}

        # These should all be list types (Union[str, SequenceNotStr[str]])
        assert field_map["id"].is_list_type is True
        assert field_map["name"].is_list_type is True
        assert field_map["namespace"].is_list_type is True
        assert field_map["description"].is_list_type is True

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_filter_fields_without_sequence_are_not_list_types(self):
        """Filter fields with simple str type should not be list types."""
        from nemo_platform.types.dataset_filter_param import DatasetFilterParam

        fields = introspect_typed_dict(DatasetFilterParam)
        field_map = {f.name: f for f in fields}

        # These should NOT be list types (just str)
        assert field_map["namespace"].is_list_type is False
        assert field_map["project"].is_list_type is False

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_iterable_int_is_list_type(self):
        """Union[int, Iterable[int]] should be detected as list type."""
        from nemo_platform.types.dataset_search_param import DatasetSearchParam

        fields = introspect_typed_dict(DatasetSearchParam)
        field_map = {f.name: f for f in fields}

        # limit has Union[int, Iterable[int]]
        assert field_map["limit"].is_list_type is True


class TestTypedDictFieldIsSimpleCliType:
    """Tests for TypedDictField.is_simple_cli_type detection."""

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_str_fields_are_simple(self):
        """String fields should be detected as simple CLI types."""
        from nemo_platform.types.dataset_filter_param import DatasetFilterParam

        fields = introspect_typed_dict(DatasetFilterParam)
        field_map = {f.name: f for f in fields}

        assert field_map["namespace"].is_simple_cli_type is True
        assert field_map["project"].is_simple_cli_type is True

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_int_fields_are_simple(self):
        """Integer fields should be detected as simple CLI types."""
        from nemo_platform.types.customization.customization_job_list_filter_param import (
            CustomizationJobListFilterParam,
        )

        fields = introspect_typed_dict(CustomizationJobListFilterParam)
        field_map = {f.name: f for f in fields}

        assert field_map["batch_size"].is_simple_cli_type is True
        assert field_map["epochs"].is_simple_cli_type is True

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_enum_types_are_simple(self):
        """Enum-like types (PascalCase identifiers) should be detected as simple CLI types."""
        from nemo_platform.types.customization.customization_job_list_filter_param import (
            CustomizationJobListFilterParam,
        )

        fields = introspect_typed_dict(CustomizationJobListFilterParam)
        field_map = {f.name: f for f in fields}

        # These are enum types: FinetuningType, JobStatus, TrainingType
        assert field_map["finetuning_type"].is_simple_cli_type is True
        assert field_map["status"].is_simple_cli_type is True
        assert field_map["training_type"].is_simple_cli_type is True

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_complex_types_are_not_simple(self):
        """Complex nested types should NOT be detected as simple CLI types."""
        from nemo_platform.types.dataset_search_param import DatasetSearchParam

        fields = introspect_typed_dict(DatasetSearchParam)
        field_map = {f.name: f for f in fields}

        # DateRange is a nested type with start/end fields
        assert field_map["created_at"].is_simple_cli_type is False
        assert field_map["updated_at"].is_simple_cli_type is False

        # Dict types are complex
        assert field_map["custom_fields"].is_simple_cli_type is False


class TestExplodableTypedDict:
    """Tests for detecting explodable TypedDict params (filter/search)."""

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_filter_param_is_explodable(self):
        """Filter params should be detected as explodable TypedDicts."""
        introspector = SDKIntrospector()
        methods = introspector.introspect_resource(["datasets"])
        list_method = methods["list"]

        filter_param = next(p for p in list_method.optional_parameters if p.name == "filter")
        assert filter_param.is_explodable_typed_dict is True

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_search_param_is_explodable(self):
        """Search params should be detected as explodable TypedDicts."""
        introspector = SDKIntrospector()
        methods = introspector.introspect_resource(["datasets"])
        list_method = methods["list"]

        search_param = next(p for p in list_method.optional_parameters if p.name == "search")
        assert search_param.is_explodable_typed_dict is True

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_sort_param_is_not_explodable(self):
        """Sort params (simple enums) should NOT be detected as explodable."""
        introspector = SDKIntrospector()
        methods = introspector.introspect_resource(["datasets"])
        list_method = methods["list"]

        sort_param = next(p for p in list_method.optional_parameters if p.name == "sort")
        assert sort_param.is_explodable_typed_dict is False

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_page_param_is_not_explodable(self):
        """Simple params like page should NOT be explodable."""
        introspector = SDKIntrospector()
        methods = introspector.introspect_resource(["datasets"])
        list_method = methods["list"]

        page_param = next(p for p in list_method.optional_parameters if p.name == "page")
        assert page_param.is_explodable_typed_dict is False


class TestTypedDictFieldExtraction:
    """Tests for extracting fields from TypedDict classes."""

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_extract_filter_fields(self):
        """Should correctly extract fields from filter TypedDict."""
        from nemo_platform.types.dataset_filter_param import DatasetFilterParam

        fields = introspect_typed_dict(DatasetFilterParam)
        field_names = {f.name for f in fields}

        assert "namespace" in field_names
        assert "project" in field_names

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_extract_search_fields(self):
        """Should correctly extract fields from search TypedDict."""
        from nemo_platform.types.dataset_search_param import DatasetSearchParam

        fields = introspect_typed_dict(DatasetSearchParam)
        field_names = {f.name for f in fields}

        assert "id" in field_names
        assert "name" in field_names
        assert "namespace" in field_names
        assert "description" in field_names
        assert "created_at" in field_names
        assert "updated_at" in field_names

    @pytest.mark.skip(reason="TODO: Update tests after SDK changes.")
    def test_all_search_fields_have_evaluated_type(self):
        """All fields should have evaluated_type set for proper type detection."""
        from nemo_platform.types.dataset_search_param import DatasetSearchParam

        fields = introspect_typed_dict(DatasetSearchParam)

        for field in fields:
            assert field.evaluated_type is not None, f"Field {field.name} should have evaluated_type"
