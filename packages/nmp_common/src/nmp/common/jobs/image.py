# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Image helper utilities for NeMo Platform.

Provides a centralized way to build qualified Docker image names from the
platform configuration.
"""

from nmp.common.config import get_platform_config


def get_qualified_image(name: str, tag: str | None = None, registry: str | None = None) -> str:
    """Get a fully qualified Docker image name.

    Builds an image reference in the format: {registry}/{name}:{tag}

    Args:
        name: The image name (e.g., 'nmp-api', 'nmp-cpu-tasks').
        tag: Optional tag override. If not provided, uses platform config's image_tag.
        registry: Optional registry override. If not provided, uses platform config's image_registry.

    Returns:
        Fully qualified image name (e.g., 'my-registry/nmp-api:local').

    Example:
        >>> get_qualified_image("nmp-api")
        'my-registry/nmp-api:local'  # uses platform config defaults

        >>> get_qualified_image("nmp-api", tag="v1.0.0")
        'my-registry/nmp-api:v1.0.0'

        >>> get_qualified_image("nmp-api", registry="nvcr.io/nvidia/nemo-microservices", tag="25.10")
        'nvcr.io/nvidia/nemo-microservices/nmp-api:25.10'
    """
    config = get_platform_config()

    effective_registry = registry if registry is not None else config.image_registry
    effective_tag = tag if tag is not None else config.image_tag

    return f"{effective_registry}/{name}:{effective_tag}"


def image_builder(registry: str | None = None, tag: str | None = None):
    """Create a function that builds qualified image names with preset registry and tag.

    Useful when you need to build multiple image names with the same registry/tag.

    Args:
        registry: Optional registry override. If not provided, uses platform config's image_registry.
        tag: Optional tag override. If not provided, uses platform config's image_tag.

    Returns:
        A function that takes an image name and returns the fully qualified image.

    Example:
        >>> build_image = image_builder()
        >>> build_image("nmp-api")
        'my-registry/nmp-api:local'
        >>> build_image("nmp-cpu-tasks")
        'my-registry/nmp-cpu-tasks:local'

        >>> build_image = image_builder(registry="nvcr.io/nvidia", tag="v1.0")
        >>> build_image("nmp-api")
        'nvcr.io/nvidia/nmp-api:v1.0'
    """
    config = get_platform_config()

    effective_registry = registry if registry is not None else config.image_registry
    effective_tag = tag if tag is not None else config.image_tag

    def _build(name: str) -> str:
        return f"{effective_registry}/{name}:{effective_tag}"

    return _build
