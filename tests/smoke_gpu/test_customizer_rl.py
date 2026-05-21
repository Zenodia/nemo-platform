# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Customizer RL image import smoke tests.

Built as part of the docker-customizer bake group (smoke-test stage) and run
on a CPU runner — no GPU hardware required.

Two failure classes are caught at .so load time, before any GPU device is touched:

  ModuleNotFoundError  — package missing from the image (e.g. excluded from
                         a tar layer without a compensating COPY command)

  ImportError          — CUDA extension .so has an undefined symbol; the wheel
                         was compiled against a different PyTorch version than
                         the one installed (ABI mismatch)
"""

import pytest

pytestmark = pytest.mark.smoke_customizer_rl


def test_torch_importable():
    import torch  # noqa: F401


def test_ray_importable():
    import ray  # noqa: F401


def test_nmp_customizer_importable():
    import nmp.customizer  # noqa: F401
