# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
NeMo Platform Error Mapping Library
=========================

A generic, reusable framework for converting exceptions from one domain to another.
Each service maintains its own rules; this library provides the core abstraction.

Quick Start
-----------
    from nmp.common.errors import RulesLoader

    # Define your exception registry
    EXCEPTION_REGISTRY = {
        "ModelLoadError": ModelLoadError,
        "CudaError": CudaError,
    }

    # Load converter from YAML
    converter = RulesLoader.from_yaml(
        "error_rules.yaml",
        exception_registry=EXCEPTION_REGISTRY,
    )

    # Convert exceptions
    try:
        risky_operation()
    except Exception as e:
        converter.raise_converted_or_original(e)

See design.md in this package for full architecture documentation.
"""

from nmp.common.errors.converter import ExceptionConverter
from nmp.common.errors.loader import RulesLoader
from nmp.common.errors.matchers import (
    # Keyword matchers
    AllKeywordsMatcher,
    AnyKeywordMatcher,
    AttributeMatcher,
    # Special matchers
    CauseMatcher,
    # Composite matchers
    CompositeMatcher,
    ContainsMatcher,
    EndsWithMatcher,
    # Basic matchers
    ExactMatcher,
    # Abstract base
    ExceptionMatcher,
    # Type-based matchers
    ExceptionTypeMatcher,
    ExceptionTypeNameMatcher,
    NotMatcher,
    OrMatcher,
    RegexMatcher,
    StartsWithMatcher,
)
from nmp.common.errors.sdk_exception_handlers import (
    register_sdk_exception_handlers,
    sdk_status_error_handler,
)
from nmp.common.errors.types import (
    DefaultExceptionHandler,
    ExceptionRegistry,
    Handler,
    HandlerRegistry,
)

__all__ = [
    # SDK exception handlers
    "register_sdk_exception_handlers",
    "sdk_status_error_handler",
    # Matchers
    "AllKeywordsMatcher",
    "AnyKeywordMatcher",
    "AttributeMatcher",
    "CauseMatcher",
    "CompositeMatcher",
    "ContainsMatcher",
    "EndsWithMatcher",
    "ExactMatcher",
    "ExceptionMatcher",
    "ExceptionTypeMatcher",
    "ExceptionTypeNameMatcher",
    "NotMatcher",
    "OrMatcher",
    "RegexMatcher",
    "StartsWithMatcher",
    # Core classes
    "ExceptionConverter",
    "RulesLoader",
    # Type aliases
    "DefaultExceptionHandler",
    "ExceptionRegistry",
    "Handler",
    "HandlerRegistry",
]
