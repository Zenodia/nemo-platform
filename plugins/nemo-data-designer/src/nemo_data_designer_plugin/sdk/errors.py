# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from data_designer.errors import DataDesignerError


class DataDesignerClientError(DataDesignerError):
    """Base exception for Data Designer client errors."""


class DataDesignerConfigValidationError(DataDesignerClientError):
    """Exception raised when the Data Designer configuration is invalid."""


class DataDesignerPreviewError(DataDesignerClientError):
    """Raised for errors related to a Data Designer preview request."""


class DataDesignerJobError(DataDesignerClientError):
    """Raised for errors related to a Data Designer job."""
