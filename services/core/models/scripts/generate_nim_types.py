#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generate Pydantic models from k8s-nim-operator CRD definitions."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

# Configuration: CRDs to process
# Each tuple is (crd_filename, class_name)
# see: https://github.com/NVIDIA/k8s-nim-operator/tree/main/config/crd/bases
CRDS_TO_PROCESS = [
    ("apps.nvidia.com_nimservices.yaml", "NIMService"),
    ("apps.nvidia.com_nimcaches.yaml", "NIMCache"),
]


def extract_openapi_schema(crd_path: Path) -> dict:
    """Extract OpenAPI v3 schema from CRD YAML."""
    crd = yaml.safe_load(crd_path.read_text())
    versions = crd["spec"]["versions"]
    if not versions:
        raise ValueError(f"No versions in {crd_path.name}")
    return versions[0]["schema"]["openAPIV3Schema"]


def fix_kubernetes_int_or_string_types(content: str) -> str:
    """Fix Kubernetes IntOrString types that have pattern constraints on Union[int, str].

    The datamodel-code-generator doesn't handle x-kubernetes-int-or-string properly,
    generating types like Union[int, str] with a pattern constraint that only applies
    to strings. This causes Pydantic validation errors when integers are passed.

    We fix this by removing the pattern constraint from RootModel types.
    """
    import re

    # Pattern to match RootModel classes with Field(..., pattern=..., ...)
    # We need to match the complete Field() call including description and pattern
    # Example:
    # class Limits(RootModel[int]):
    #     root: int = Field(
    #         ...,
    #         description="...",
    #         pattern='^...$',
    #     )
    pattern = re.compile(
        r"class\s+(\w+)\(RootModel\[(int|str)\]\):\n"
        r"\s+root:\s+(int|str)\s+=\s+Field\(\n"
        r"(?:\s+\.\.\..*?\n)?"  # Ellipsis line (optional)
        r"(?:\s+description=.*?\n)?"  # Description line (optional)
        r"\s+pattern=.*?\n"  # Pattern line
        r"\s+\)",  # Closing paren
        re.MULTILINE,
    )

    def replace_root_model(match):
        class_name = match.group(1)
        type_name = match.group(2)
        # Return simplified version without Field and pattern
        return f"class {class_name}(RootModel[{type_name}]):\n    root: {type_name}"

    return pattern.sub(replace_root_model, content)


def generate_pydantic_models(schema: dict, output_file: Path, class_name: str, version: str = "unknown"):
    """Generate Pydantic models using datamodel-code-generator."""
    temp_schema = output_file.parent / "temp_schema.json"

    openapi_doc = {
        "openapi": "3.0.0",
        "info": {"title": f"{class_name} Schema", "version": "1.0.0"},
        "components": {"schemas": {class_name: schema}},
    }

    temp_schema.write_text(json.dumps(openapi_doc, indent=2))

    try:
        cmd = [
            "uv",
            "run",
            "datamodel-codegen",
            "--input",
            str(temp_schema),
            "--output",
            str(output_file),
            "--input-file-type",
            "openapi",
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--field-constraints",
            "--use-standard-collections",
            "--use-schema-description",
            "--use-title-as-name",
            "--target-python-version",
            "3.11",
        ]

        subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Read generated content
        content = output_file.read_text()

        # Fix Kubernetes IntOrString types
        content = fix_kubernetes_int_or_string_types(content)

        # Add version header to generated file
        header = f"# Generated from k8s-nim-operator {version}\n# Source: https://github.com/NVIDIA/k8s-nim-operator\n"
        output_file.write_text(header + content)

        print(f"Generated: {output_file.name}")
    finally:
        temp_schema.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Generate Pydantic models from k8s-nim-operator CRDs")
    parser.add_argument("--version", default="unknown", help="k8s-nim-operator version tag")
    args = parser.parse_args()
    version = args.version

    script_dir = Path(__file__).parent
    models_dir = script_dir.parent
    operator_dir = models_dir / "k8s-nim-operator"
    crd_dir = operator_dir / "config" / "crd" / "bases"
    output_dir = models_dir / "src" / "models" / "nim_operator_types"

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating Pydantic models from k8s-nim-operator {version}")
    print("-" * 60)

    for crd_filename, class_name in CRDS_TO_PROCESS:
        crd_path = crd_dir / crd_filename
        output_file = output_dir / f"{class_name.lower()}.py"

        try:
            schema = extract_openapi_schema(crd_path)
            generate_pydantic_models(schema, output_file, class_name, version)
        except Exception as e:
            print(f"Error processing {class_name}: {e}", file=sys.stderr)
            sys.exit(1)

    # Generate __init__.py
    imports = "\n".join(
        f"from nmp.core.models.controllers.backends.k8s_nim_operator.types.{cls.lower()} import {cls}"
        for _, cls in CRDS_TO_PROCESS
    )
    exports = [cls for _, cls in CRDS_TO_PROCESS]

    init_content = f'''# Generated from k8s-nim-operator {version}
# Source: https://github.com/NVIDIA/k8s-nim-operator
"""Generated Pydantic models from k8s-nim-operator CRDs."""

{imports}

__all__ = {exports}
'''

    init_file = output_dir / "__init__.py"
    init_file.write_text(init_content)
    print(f"Generated: {init_file.name}")
    print("-" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
