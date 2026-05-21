# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0


class AnonymizerInternalError(Exception):
    """Unexpected internal error during anonymizer plugin execution."""


class AnonymizerInvalidConfigError(Exception):
    """The anonymizer plugin received a config the platform considers invalid."""
