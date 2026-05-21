# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Entry point for running the file-io task as a module."""

import sys

from nmp.customizer.tasks.file_io import run

if __name__ == "__main__":
    sys.exit(run())
