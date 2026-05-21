# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for Ray cluster bootstrap functionality.

Tests the RayClusterBootstrap class which provides Python equivalent of run-ray.sh
for bootstrapping Ray clusters on Volcano-provisioned pods.
"""

import os
import threading
import time
from pathlib import Path

import pytest
from nmp.customizer.tasks.training.backends.nemo_rl.ray_bootstrap import (
    RayClusterBootstrap,
    RayPortConfig,
    create_bootstrap_from_env,
)
from pytest_mock import MockerFixture


class TestRayPortConfig:
    """Tests for RayPortConfig dataclass."""

    def test_default_ports(self) -> None:
        """Test default port values are set correctly."""
        config = RayPortConfig()

        assert config.node_manager_port == 53001
        assert config.object_manager_port == 53003
        assert config.runtime_env_agent_port == 53005
        assert config.dashboard_agent_grpc_port == 53007
        assert config.metrics_export_port == 53009
        assert config.gcs_port == 6379
        assert config.ray_client_server_port == 10001
        assert config.dashboard_port == 8265
        assert config.dashboard_agent_listen_port == 52365
        assert config.min_worker_port == 54001
        assert config.max_worker_port == 54257

    def test_ports_from_env(self, mocker: MockerFixture) -> None:
        """Test ports can be configured via environment variables."""
        mocker.patch.dict(
            "os.environ",
            {
                "NODE_MANAGER_PORT": "60001",
                "GCS_PORT": "7000",
                "DASHBOARD_PORT": "9000",
            },
        )

        config = RayPortConfig()

        assert config.node_manager_port == 60001
        assert config.gcs_port == 7000
        assert config.dashboard_port == 9000


class TestRayClusterBootstrapInit:
    """Tests for RayClusterBootstrap initialization."""

    def test_basic_init(self, tmp_path: Path) -> None:
        """Test basic initialization with required parameters."""
        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=2,
            master_addr="192.168.1.1",
            log_dir=tmp_path / "logs",
        )

        assert bootstrap.rank == 0
        assert bootstrap.world_size == 2
        assert bootstrap.master_addr == "192.168.1.1"
        assert bootstrap.gpus_per_node >= 1
        assert bootstrap.log_dir.exists()

    def test_proxy_env_unset(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test that proxy environment variables are unset on init."""
        mocker.patch.dict(
            "os.environ",
            {
                "http_proxy": "http://proxy:8080",
                "https_proxy": "https://proxy:8080",
                "HTTP_PROXY": "http://proxy:8080",
                "HTTPS_PROXY": "https://proxy:8080",
            },
        )

        RayClusterBootstrap(
            rank=0,
            world_size=1,
            master_addr="localhost",
            log_dir=tmp_path / "logs",
        )

        # Proxy vars should be removed
        assert "http_proxy" not in os.environ
        assert "https_proxy" not in os.environ
        assert "HTTP_PROXY" not in os.environ
        assert "HTTPS_PROXY" not in os.environ

    def test_expected_worker_units(self, tmp_path: Path) -> None:
        """Test expected_worker_units property calculation."""
        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=4,
            master_addr="localhost",
            gpus_per_node=8,
            log_dir=tmp_path / "logs",
        )

        assert bootstrap.expected_worker_units == 32  # 4 nodes * 8 GPUs

    def test_max_wait_single_node(self, tmp_path: Path) -> None:
        """Test max_wait_seconds for single node cluster."""
        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=1,
            master_addr="localhost",
            log_dir=tmp_path / "logs",
        )

        assert bootstrap.max_wait_seconds == 240  # 4 minutes

    def test_max_wait_multi_node(self, tmp_path: Path) -> None:
        """Test max_wait_seconds for multi-node cluster."""
        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=4,
            master_addr="localhost",
            log_dir=tmp_path / "logs",
        )

        assert bootstrap.max_wait_seconds == 2400  # 40 minutes


class TestParseWorkerUnits:
    """Tests for _parse_worker_units static method.

    The ray status output format is: usage/total resource_name
    Example: " 0.0/1.0 worker_units"

    We parse the TOTAL (second number) as that represents available capacity.
    """

    @pytest.mark.parametrize(
        "status_output,expected_total",
        [
            # Standard format with decimals - returns TOTAL (second number)
            ("0.0/4.0 worker_units", 4),
            ("2.0/8.0 worker_units", 8),
            # Fully utilized cluster
            ("8.0/8.0 worker_units", 8),
            # Integer format
            ("0/8 worker_units", 8),
            # With surrounding text (realistic ray status output)
            (
                "Resources\n"
                "---------------------------------------------------------------\n"
                "Total Usage:\n"
                " 0.0/255.0 CPU\n"
                " 0.0/1.0 GPU\n"
                " 0B/1.95TiB memory\n"
                " 0.0/32.0 worker_units\n",
                32,
            ),
            # Single node cluster
            ("0.0/1.0 worker_units", 1),
            # Large multi-node cluster
            ("64.0/256.0 worker_units", 256),
        ],
    )
    def test_parse_worker_units_success(self, status_output: str, expected_total: int) -> None:
        """Test successful parsing of worker_units total from ray status output."""
        result = RayClusterBootstrap._parse_worker_units(status_output)
        assert result == expected_total

    @pytest.mark.parametrize(
        "status_output",
        [
            "",  # Empty output
            "No cluster running",  # No worker_units line
            "Resources\nCPU: 64/128\nGPU: 8/8\n",  # Missing worker_units
            "worker_units:",  # Incomplete line
        ],
    )
    def test_parse_worker_units_no_match(self, status_output: str) -> None:
        """Test parsing returns 0 when worker_units not found."""
        result = RayClusterBootstrap._parse_worker_units(status_output)
        assert result == 0


class TestHeadNodeStartup:
    """Tests for head node startup functionality."""

    def test_start_head_process_command(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test head node start command includes all required arguments."""
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_run = mocker.patch("subprocess.run", return_value=mock_result)

        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=2,
            master_addr="10.0.0.1",
            gpus_per_node=4,
            log_dir=tmp_path / "logs",
        )

        result = bootstrap._start_head_process()

        assert result is not None
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]

        # Head uses port+1 offset for manager ports
        # Note: --block is NOT included since subprocess.run doesn't need it
        p = bootstrap.ports
        expected_cmd = [
            bootstrap.ray_executable,  # Derived from driver_python
            "start",
            "--head",
            "--disable-usage-stats",
            "--include-dashboard=false",
            '--resources={"worker_units": 4}',
            "--node-ip-address=10.0.0.1",
            f"--port={p.gcs_port}",
            f"--ray-client-server-port={p.ray_client_server_port}",
            f"--dashboard-port={p.dashboard_port}",
            f"--node-manager-port={p.node_manager_port + 1}",
            f"--object-manager-port={p.object_manager_port + 1}",
            f"--runtime-env-agent-port={p.runtime_env_agent_port + 1}",
            f"--dashboard-agent-grpc-port={p.dashboard_agent_grpc_port + 1}",
            f"--dashboard-agent-listen-port={p.dashboard_agent_listen_port + 1}",
            f"--metrics-export-port={p.metrics_export_port + 1}",
        ]
        assert cmd == expected_cmd


class TestWorkerNodeStartup:
    """Tests for worker node startup functionality."""

    def test_start_worker_process_command(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test worker node start command includes all required arguments."""
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_run = mocker.patch("subprocess.run", return_value=mock_result)

        bootstrap = RayClusterBootstrap(
            rank=1,
            world_size=2,
            master_addr="10.0.0.1",
            gpus_per_node=4,
            log_dir=tmp_path / "logs",
        )

        result = bootstrap._start_worker_process()

        assert result is not None
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]

        # Workers use base ports (no +1 offset)
        # Note: --block is NOT included since subprocess.run doesn't need it
        p = bootstrap.ports
        expected_cmd = [
            bootstrap.ray_executable,  # Derived from driver_python
            "start",
            f"--address=10.0.0.1:{p.gcs_port}",
            "--disable-usage-stats",
            '--resources={"worker_units": 4}',
            f"--min-worker-port={p.min_worker_port}",
            f"--max-worker-port={p.max_worker_port}",
            f"--node-manager-port={p.node_manager_port}",
            f"--object-manager-port={p.object_manager_port}",
            f"--runtime-env-agent-port={p.runtime_env_agent_port}",
            f"--dashboard-agent-grpc-port={p.dashboard_agent_grpc_port}",
            f"--dashboard-agent-listen-port={p.dashboard_agent_listen_port}",
            f"--metrics-export-port={p.metrics_export_port}",
        ]
        assert cmd == expected_cmd


class TestWaitForWorkers:
    """Tests for waiting for workers to connect."""

    def test_wait_for_workers_success(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test wait_for_workers succeeds when all workers connect."""
        # Mock ray status to return increasing worker counts
        # Format: "usage/total worker_units" - we check that total >= expected
        call_count = 0

        def mock_run(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1
            result = mocker.MagicMock()
            result.returncode = 0
            # First call: partial cluster (only 4 of 8 worker_units available)
            # Second call: full cluster (all 8 worker_units available)
            if call_count < 2:
                result.stdout = "0.0/4.0 worker_units"  # Only 4 total
            else:
                result.stdout = "0.0/8.0 worker_units"  # All 8 total
            return result

        mocker.patch("subprocess.run", side_effect=mock_run)
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.ray_bootstrap._pause")

        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=2,
            master_addr="localhost",
            gpus_per_node=4,
            log_dir=tmp_path / "logs",
        )

        # Should complete without raising (expects 8 worker_units = 2 nodes * 4 GPUs)
        bootstrap._wait_for_workers()

    def test_wait_for_workers_timeout(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test wait_for_workers raises TimeoutError when workers don't connect."""
        # Mock ray status to always return partial cluster (only 4 of 8 needed)
        # Format: "usage/total worker_units"
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "0.0/4.0 worker_units"  # Only 4 total, need 8
        mocker.patch("subprocess.run", return_value=mock_result)
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.ray_bootstrap._pause")
        # Set very short timeout for test
        mocker.patch.object(RayClusterBootstrap, "max_wait_seconds", new_callable=mocker.PropertyMock, return_value=4)

        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=2,
            master_addr="localhost",
            gpus_per_node=4,
            log_dir=tmp_path / "logs",
        )

        with pytest.raises(TimeoutError, match="Timed out waiting"):
            bootstrap._wait_for_workers()


class TestTerminationSignaling:
    """Tests for ENDED file termination signaling."""

    def test_signal_termination_creates_ended_file(self, tmp_path: Path) -> None:
        """Test _signal_termination creates ENDED file."""
        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=1,
            master_addr="localhost",
            log_dir=tmp_path / "logs",
        )

        assert not bootstrap.ended_file.exists()

        bootstrap._signal_termination()

        assert bootstrap.ended_file.exists()

    def test_ended_file_path(self, tmp_path: Path) -> None:
        """Test ended_file property returns correct path."""
        log_dir = tmp_path / "custom_logs"
        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=1,
            master_addr="localhost",
            log_dir=log_dir,
        )

        assert bootstrap.ended_file == log_dir / "ENDED"


class TestCleanup:
    """Tests for cleanup functionality."""

    def test_cleanup_creates_ended_file(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test cleanup creates ENDED file and stops Ray."""
        mock_run = mocker.patch("subprocess.run")

        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=1,
            master_addr="localhost",
            log_dir=tmp_path / "logs",
        )

        bootstrap._cleanup_with_timeout(timeout=1)

        # ENDED file should be created
        assert bootstrap.ended_file.exists()

        # ray stop should be called (ray_executable is first element, "stop" is second)
        stop_calls = [
            call
            for call in mock_run.call_args_list
            if len(call[0][0]) >= 2 and call[0][0][0] == bootstrap.ray_executable and "stop" in call[0][0]
        ]
        assert len(stop_calls) >= 1

    def test_stop_ray_with_grace_period(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test _stop_ray passes correct grace period."""
        mock_run = mocker.patch("subprocess.run")

        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=1,
            master_addr="localhost",
            log_dir=tmp_path / "logs",
        )

        bootstrap._stop_ray(grace_period=30)

        expected_cmd = [bootstrap.ray_executable, "stop", "--force", "--grace-period=30"]
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd == expected_cmd


class TestCreateBootstrapFromEnv:
    """Tests for create_bootstrap_from_env factory function."""

    def test_create_from_env_defaults(self, mocker: MockerFixture) -> None:
        """Test creation with default environment values."""
        mocker.patch.dict("os.environ", {}, clear=True)

        bootstrap = create_bootstrap_from_env()

        assert bootstrap.rank == 0
        assert bootstrap.world_size == 1
        assert bootstrap.master_addr == "127.0.0.1"

    def test_create_from_env_custom(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test creation with custom environment values."""
        mocker.patch.dict(
            "os.environ",
            {
                "RANK": "3",
                "WORLD_SIZE": "8",
                "MASTER_ADDR": "10.0.0.100",
                "GPUS_PER_NODE": "4",
                "BASE_LOG_DIR": str(tmp_path / "custom" / "logs"),
            },
        )

        bootstrap = create_bootstrap_from_env()

        assert bootstrap.rank == 3
        assert bootstrap.world_size == 8
        assert bootstrap.master_addr == "10.0.0.100"
        assert bootstrap.gpus_per_node == 4


class TestDriverExecution:
    """Tests for driver script execution."""

    @staticmethod
    def _make_mock_popen(mocker: MockerFixture, *, returncode: int = 0) -> "MagicMock":  # noqa: F821
        """Create a mock Popen whose stdout immediately signals EOF."""
        mock_proc = mocker.MagicMock()
        mock_proc.returncode = returncode
        mock_proc.pid = 12345
        mock_proc.stdout.readline.return_value = ""
        mock_proc.wait.return_value = returncode
        return mock_proc

    def test_run_driver_success(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test _run_driver executes driver script and returns exit code."""
        mock_proc = self._make_mock_popen(mocker, returncode=0)
        mock_popen = mocker.patch("subprocess.Popen", return_value=mock_proc)
        driver_python = "/opt/venv/bin/python"

        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=1,
            master_addr="localhost",
            log_dir=tmp_path / "logs",
            driver_python=driver_python,
        )

        exit_code = bootstrap._run_driver("/path/to/driver.py", ["--config", "config.yaml", "--id", "job-123"])

        expected_cmd = [
            driver_python,
            "/path/to/driver.py",
            "--config",
            "config.yaml",
            "--id",
            "job-123",
        ]
        assert exit_code == 0
        mock_popen.assert_called_once()
        cmd = mock_popen.call_args[0][0]
        assert cmd == expected_cmd

    def test_run_driver_failure(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test _run_driver returns non-zero exit code on failure."""
        mock_proc = self._make_mock_popen(mocker, returncode=1)
        mocker.patch("subprocess.Popen", return_value=mock_proc)

        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=1,
            master_addr="localhost",
            log_dir=tmp_path / "logs",
        )

        exit_code = bootstrap._run_driver("/path/to/driver.py", [])

        assert exit_code == 1


class TestIntegrationHeadFlow:
    """Integration tests for head node flow."""

    def test_head_with_driver_full_flow(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test full head node flow: start -> wait -> driver -> cleanup."""
        call_sequence: list[tuple[str, list[str]]] = []

        bootstrap = RayClusterBootstrap(
            rank=0,
            world_size=1,
            master_addr="localhost",
            gpus_per_node=4,
            log_dir=tmp_path / "logs",
        )

        def mock_run(cmd, **_kwargs):
            call_sequence.append(("run", cmd[:3] if isinstance(cmd, list) else [cmd]))
            result = mocker.MagicMock()
            result.returncode = 0
            if isinstance(cmd, list):
                if cmd[0] == bootstrap.ray_executable and "status" in cmd:
                    result.stdout = "0.0/4.0 worker_units"
            return result

        mocker.patch("subprocess.run", side_effect=mock_run)
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.ray_bootstrap._pause")

        mock_proc = mocker.MagicMock()
        mock_proc.returncode = 0
        mock_proc.pid = 12345
        mock_proc.stdout.readline.return_value = ""
        mock_proc.wait.return_value = 0
        mocker.patch("subprocess.Popen", return_value=mock_proc)

        exit_code = bootstrap.run_with_driver(
            "/path/to/dpo_driver.py",
            ["--config", "/path/to/config.yaml"],
        )

        assert exit_code == 0
        assert bootstrap.ended_file.exists()

        ray_start_calls = [
            c
            for c in call_sequence
            if c[0] == "run" and len(c[1]) >= 2 and c[1][0] == bootstrap.ray_executable and c[1][1] == "start"
        ]
        assert len(ray_start_calls) >= 1


class TestIntegrationWorkerFlow:
    """Integration tests for worker node flow."""

    def test_worker_termination_on_ended_file(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test worker exits gracefully when ENDED file is created."""
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mocker.patch("subprocess.run", return_value=mock_result)

        bootstrap = RayClusterBootstrap(
            rank=1,
            world_size=2,
            master_addr="localhost",
            log_dir=tmp_path / "logs",
        )

        # Create ENDED file after short delay
        def create_ended_file():
            time.sleep(0.1)
            bootstrap._signal_termination()

        threading.Thread(target=create_ended_file).start()

        # Should exit when ENDED file detected
        exit_code = bootstrap._monitor_for_termination()

        assert exit_code == 0
