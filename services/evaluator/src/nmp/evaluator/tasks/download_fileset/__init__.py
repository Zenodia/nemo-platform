# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Download fileset task package.

This task downloads datasets from filesets to the local filesystem.
"""

from nmp.evaluator.tasks.download_fileset.__main__ import run

__all__ = ["run"]
