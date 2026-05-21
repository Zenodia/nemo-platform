# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for distributed training coordination utilities.

These tests are CPU-safe and run in regular CI - no GPU dependencies.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

import pytest
from nmp.customizer.tasks.training.distributed import (
    RANK_ENVVAR,
    WORLD_SIZE_ENVVAR,
    DistributedContext,
    DistributedRole,
)

# Test barrier names
TEST_BARRIER = "test_barrier"
TEST_SYNC = "test_sync"


@pytest.fixture
def barrier_dir(tmp_path: Path) -> Path:
    """Create and return a barrier directory for tests."""
    path = tmp_path / "barriers"
    path.mkdir(parents=True)
    return path


class TestDistributedContext:
    """Tests for DistributedContext class."""

    def test_single_node_defaults(self, barrier_dir: Path):
        """Test default single-node configuration (no env vars set)."""
        # Clear env vars if set
        with mock.patch.dict(os.environ, {}, clear=True):
            ctx = DistributedContext.from_env(barrier_dir)

        assert ctx.rank == 0
        assert ctx.world_size == 1
        assert ctx.role == DistributedRole.COORDINATOR
        assert ctx.is_coordinator is True
        assert ctx.is_distributed is False

    def test_coordinator_role_from_env(self, barrier_dir: Path):
        """Test coordinator detection from RANK=0."""
        with mock.patch.dict(os.environ, {RANK_ENVVAR: "0", WORLD_SIZE_ENVVAR: "2"}):
            ctx = DistributedContext.from_env(barrier_dir)

        assert ctx.rank == 0
        assert ctx.world_size == 2
        assert ctx.role == DistributedRole.COORDINATOR
        assert ctx.is_coordinator is True
        assert ctx.is_distributed is True

    def test_worker_role_from_env(self, barrier_dir: Path):
        """Test worker detection from RANK > 0."""
        with mock.patch.dict(os.environ, {RANK_ENVVAR: "1", WORLD_SIZE_ENVVAR: "2"}):
            ctx = DistributedContext.from_env(barrier_dir)

        assert ctx.rank == 1
        assert ctx.world_size == 2
        assert ctx.role == DistributedRole.WORKER
        assert ctx.is_coordinator is False
        assert ctx.is_distributed is True


class TestBarrierSignaling:
    """Tests for file-based barrier synchronization."""

    def test_signal_creates_marker_file(self, barrier_dir: Path):
        """Test that signal() creates a marker file."""
        ctx = DistributedContext(
            role=DistributedRole.COORDINATOR,
            rank=0,
            world_size=2,
            barrier_dir=barrier_dir,
        )

        ctx.signal(TEST_BARRIER)

        marker = barrier_dir / f"{TEST_BARRIER}.rank0.ready"
        assert marker.exists()

    def test_signal_noop_for_single_node(self, tmp_path: Path):
        """Test that signal() is a no-op for single-node mode."""
        # Use tmp_path directly (not barrier_dir) to test that directory isn't created
        nonexistent_dir = tmp_path / "nonexistent_barriers"
        ctx = DistributedContext(
            role=DistributedRole.COORDINATOR,
            rank=0,
            world_size=1,  # Single node
            barrier_dir=nonexistent_dir,
        )

        ctx.signal(TEST_BARRIER)

        # No marker file should be created
        assert not nonexistent_dir.exists() or not any(nonexistent_dir.iterdir())

    def test_wait_for_coordinator_returns_immediately_for_coordinator(self, barrier_dir: Path):
        """Test that coordinator doesn't wait for itself."""
        ctx = DistributedContext(
            role=DistributedRole.COORDINATOR,
            rank=0,
            world_size=2,
            barrier_dir=barrier_dir,
        )

        # Should return immediately without blocking
        start = time.time()
        ctx.wait_for_coordinator(TEST_BARRIER, timeout=0.1)
        elapsed = time.time() - start

        assert elapsed < 0.1  # Should not have waited

    def test_wait_for_coordinator_waits_for_signal(self, barrier_dir: Path):
        """Test that worker waits for coordinator signal."""
        worker_ctx = DistributedContext(
            role=DistributedRole.WORKER,
            rank=1,
            world_size=2,
            barrier_dir=barrier_dir,
            _poll_interval=0.01,  # Fast polling for test
        )

        def signal_after_delay():
            time.sleep(0.05)
            marker = barrier_dir / f"{TEST_BARRIER}.rank0.ready"
            marker.touch()

        with ThreadPoolExecutor() as executor:
            executor.submit(signal_after_delay)
            worker_ctx.wait_for_coordinator(TEST_BARRIER, timeout=1.0)

        # Should have waited and received signal
        assert (barrier_dir / f"{TEST_BARRIER}.rank0.ready").exists()

    def test_wait_for_coordinator_timeout(self, barrier_dir: Path):
        """Test that wait_for_coordinator raises TimeoutError."""
        worker_ctx = DistributedContext(
            role=DistributedRole.WORKER,
            rank=1,
            world_size=2,
            barrier_dir=barrier_dir,
            _poll_interval=0.01,
        )

        with pytest.raises(TimeoutError, match="Timeout waiting for coordinator"):
            worker_ctx.wait_for_coordinator(TEST_BARRIER, timeout=0.05)


class TestSyncPoint:
    """Tests for sync_point (all-to-all barrier)."""

    def test_sync_point_all_ranks_arrive(self, barrier_dir: Path):
        """Test that sync_point waits for all ranks."""
        world_size = 3
        contexts = [
            DistributedContext(
                role=DistributedRole.COORDINATOR if i == 0 else DistributedRole.WORKER,
                rank=i,
                world_size=world_size,
                barrier_dir=barrier_dir,
                _poll_interval=0.01,
            )
            for i in range(world_size)
        ]

        results = []

        def sync_rank(ctx: DistributedContext):
            ctx.sync_point(TEST_SYNC, timeout=1.0)
            return ctx.rank

        with ThreadPoolExecutor(max_workers=world_size) as executor:
            futures = [executor.submit(sync_rank, ctx) for ctx in contexts]
            results = [f.result(timeout=2.0) for f in futures]

        # All ranks should have completed
        assert sorted(results) == [0, 1, 2]

    def test_sync_point_timeout_reports_missing_ranks(self, barrier_dir: Path):
        """Test that sync_point timeout message includes missing ranks."""
        ctx = DistributedContext(
            role=DistributedRole.COORDINATOR,
            rank=0,
            world_size=3,
            barrier_dir=barrier_dir,
            _poll_interval=0.01,
        )

        # Signal only rank 0
        ctx.signal(TEST_SYNC)

        with pytest.raises(TimeoutError, match=r"Missing ranks: \[1, 2\]"):
            ctx.wait_all(TEST_SYNC, timeout=0.05)


class TestBarrierCleanup:
    """Tests for barrier cleanup."""

    def test_cleanup_barrier_removes_markers(self, barrier_dir: Path):
        """Test that cleanup_barrier removes all marker files."""
        ctx = DistributedContext(
            role=DistributedRole.COORDINATOR,
            rank=0,
            world_size=3,
            barrier_dir=barrier_dir,
        )

        # Create markers for all ranks
        for r in range(3):
            (barrier_dir / f"{TEST_BARRIER}.rank{r}.ready").touch()

        ctx.cleanup_barrier(TEST_BARRIER)

        # All markers should be removed
        markers = list(barrier_dir.glob(f"{TEST_BARRIER}.rank*.ready"))
        assert len(markers) == 0

    def test_cleanup_barrier_noop_for_worker(self, barrier_dir: Path):
        """Test that cleanup_barrier is a no-op for workers."""
        ctx = DistributedContext(
            role=DistributedRole.WORKER,
            rank=1,
            world_size=2,
            barrier_dir=barrier_dir,
        )

        # Create marker
        marker = barrier_dir / f"{TEST_BARRIER}.rank0.ready"
        marker.touch()

        ctx.cleanup_barrier(TEST_BARRIER)

        # Marker should still exist (worker doesn't clean up)
        assert marker.exists()


class TestStaleBarrierCleanup:
    """Tests for stale barrier cleanup on initialization."""

    def test_coordinator_cleans_stale_barriers_on_init(self, barrier_dir: Path):
        """Test that coordinator removes stale barriers from previous runs."""
        # Simulate stale barriers from a previous run
        (barrier_dir / "old_barrier.rank0.ready").touch()
        (barrier_dir / "old_barrier.rank1.ready").touch()

        with mock.patch.dict(os.environ, {RANK_ENVVAR: "0", WORLD_SIZE_ENVVAR: "2"}):
            DistributedContext.from_env(barrier_dir)

        # Stale barriers should be cleaned up
        assert not (barrier_dir / "old_barrier.rank0.ready").exists()
        assert not (barrier_dir / "old_barrier.rank1.ready").exists()

    def test_worker_does_not_clean_barriers_on_init(self, barrier_dir: Path):
        """Test that workers don't clean barriers (coordinator handles it)."""
        # Simulate existing barriers
        (barrier_dir / "existing_barrier.rank0.ready").touch()

        with mock.patch.dict(os.environ, {RANK_ENVVAR: "1", WORLD_SIZE_ENVVAR: "2"}):
            DistributedContext.from_env(barrier_dir)

        # Barrier should still exist (worker doesn't clean up)
        assert (barrier_dir / "existing_barrier.rank0.ready").exists()
