# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shared validation logic for entity fields."""

import re
from typing import Optional

from nmp.common.entities.constants import REGEX_WORD_CHARACTER_DOT_DASH
from nmp.customizer.app.jobs.file_io.schemas import FileSetRef

# Regex pattern: fileset://{workspace}/{name}
# workspace and name should be non-empty strings without slashes
FILESET_URI_PATTERN = re.compile(r"^fileset://([^/]+)/([^/]+)$")
_NAME_REGEX = re.compile(REGEX_WORD_CHARACTER_DOT_DASH)


def validate_fileset_uri(uri: str) -> str:
    """Validate that the URI uses fileset:// protocol with {workspace}/{name} format.

    Args:
        uri: The URI string to validate.

    Returns:
        The validated URI string.

    Raises:
        ValueError: If the URI doesn't use fileset:// protocol or has invalid format.
    """
    if not uri.startswith("fileset://"):
        raise ValueError(
            f"Only 'fileset://' protocol is currently supported. Got: {uri}. "
            "Support for 'hf://' and 'ngc://' is coming soon."
        )

    if not FILESET_URI_PATTERN.match(uri):
        raise ValueError(f"Invalid fileset URI format. Expected 'fileset://{{workspace}}/{{name}}', got: {uri}")

    dataset_name = FileSetRef.extract_name(uri)
    if not _NAME_REGEX.match(dataset_name):
        raise ValueError(
            f"Invalid dataset name: '{dataset_name}'. "
            "Entity names must contain only word characters, dots, and hyphens."
        )

    return uri


def validate_optional_fileset_uri(uri: Optional[str]) -> Optional[str]:
    """Validate fileset URI, allowing None values.

    Args:
        uri: The optional URI string to validate.

    Returns:
        The validated URI string, or None if input is None.

    Raises:
        ValueError: If the URI is not None and doesn't use fileset:// protocol
            or has invalid format.
    """
    if uri is None:
        return None
    return validate_fileset_uri(uri)
