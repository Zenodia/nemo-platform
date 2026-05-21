#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Customizer OpenAPI spec generator.
Moved from services/customizer/openapi/generate_openapi_spec.py for easier integration.
"""

import os
import pathlib
import sys
from typing import Dict

import yaml
from fastapi.testclient import TestClient


def merge_openapi_schemas(main_schema: Dict, mounted_schema: Dict) -> Dict:
    """
    Merge two OpenAPI schemas with the following conditions:
    1. Prefix paths from the mounted schema with '/v1'.
    2. Do not merge tags from the mounted schema to the main schema.
    """
    # Merge paths with '/v1' prefix for the mounted schema
    main_paths = main_schema.get("paths", {})
    mounted_paths = mounted_schema.get("paths", {})
    for path, methods in mounted_paths.items():
        # Prepend '/v1' to the path
        main_paths[f"/v1{path}"] = methods
    main_schema["paths"] = main_paths

    # Merge components, if they exist
    main_components = main_schema.get("components", {})
    mounted_components = mounted_schema.get("components", {})
    for component_type in [
        "schemas",
        "responses",
        "parameters",
        "examples",
        "requestBodies",
        "headers",
        "securitySchemes",
        "links",
        "callbacks",
    ]:
        main_component_type = main_components.get(component_type, {})
        mounted_component_type = mounted_components.get(component_type, {})
        main_component_type.update(mounted_component_type)
        main_components[component_type] = main_component_type
    main_schema["components"] = main_components
    return main_schema


def generate_customizer_openapi(output_dir: str = "openapi") -> str:
    """
    Generate the customizer OpenAPI specification.

    Args:
        output_dir: Directory where to write the generated file

    Returns:
        Path to the generated file
    """
    # Add customizer to path for imports
    customizer_path = "services/customizer/src"
    if customizer_path not in sys.path:
        sys.path.insert(0, customizer_path)

    try:
        # Import customizer apps
        from customizer.main import app
        from nmp.customizer.api.v1.main import app as app_v1

        # Generate OpenAPI specs
        client = TestClient(app)
        response = client.get("/openapi.json")
        main_json = response.json()

        client = TestClient(app_v1)
        response = client.get("/openapi.json")
        v1_json = response.json()

        # Prepare output
        output_path_obj = pathlib.Path(output_dir)
        output_path_obj.mkdir(parents=True, exist_ok=True)

        output_file = output_path_obj / "customizer.generated.openapi.yaml"
        with output_file.open("w", encoding="utf-8") as fp:
            yaml.dump(
                merge_openapi_schemas(main_json, v1_json),
                fp,
                sort_keys=False,
                allow_unicode=True,
            )

        return str(output_file)

    except ImportError as e:
        raise ImportError(
            f"Failed to import customizer modules: {e}. Make sure you're running from the project root."
        ) from e


# For backward compatibility with the original click-based interface
def main(output: str = None):
    """Main function for backward compatibility."""
    if output is None:
        output = os.getcwd()
    return generate_customizer_openapi(output)
