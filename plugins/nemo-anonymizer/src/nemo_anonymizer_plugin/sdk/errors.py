# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""SDK-side errors raised by the Anonymizer plugin's client resources."""


class AnonymizerClientError(Exception):
    """Base exception for Anonymizer client errors."""


class AnonymizerConfigValidationError(AnonymizerClientError):
    """Raised when the Anonymizer configuration is invalid."""


class AnonymizerPreviewError(AnonymizerClientError):
    """Raised for errors related to an Anonymizer preview request."""


class AnonymizerJobError(AnonymizerClientError):
    """Raised for errors related to an Anonymizer job."""
