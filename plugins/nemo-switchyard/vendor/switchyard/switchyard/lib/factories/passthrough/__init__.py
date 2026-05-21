# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Passthrough recipe — single backend with default translator."""
from switchyard.lib.factories.passthrough.factory import (
    PassthroughConfig,
    PassthroughFactory,
)

__all__ = [
    "PassthroughConfig",
    "PassthroughFactory",
]
