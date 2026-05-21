# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Ray CLI flag compatibility smoke tests.

Validates that the flags constructed by ``RayClusterBootstrap`` are accepted
by the Ray binary installed in the image.  This catches deprecated or removed
CLI flags at image-build time — before they cause production failures.

Example: ``--dashboard-grpc-port`` was removed in Ray 2.x and caused
production failures before MR !7229.
"""

import subprocess

import pytest


@pytest.mark.smoke_customizer_rl
def test_ray_head_starts_with_bootstrap_flags(tmp_path):
    """Start a single-node Ray head using the exact flags from RayClusterBootstrap.

    Catches deprecated/removed Ray CLI flags at image build time.
    """
    from nmp.customizer.tasks.training.backends.nemo_rl.ray_bootstrap import (
        RayClusterBootstrap,
    )

    bootstrap = RayClusterBootstrap(
        rank=0,
        world_size=1,
        master_addr="127.0.0.1",
        gpus_per_node=1,
        log_dir=tmp_path / "ray_smoke",
    )

    try:
        result = bootstrap._start_head_process()
        assert result is not None, "ray start returned None (flag rejected or ray broken)"
        assert result.returncode == 0, f"ray start exited with code {result.returncode}"
    finally:
        subprocess.run(
            [bootstrap.ray_executable, "stop", "--force", "--grace-period=0"],
            check=False,
        )
