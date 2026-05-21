# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for _prepare_aut_config_for_runtime IGW routing logic."""

import subprocess
from pathlib import Path

import nat_runner
import pytest
import yaml
from nat_runner import (
    _agent_log_has_workflow_error,
    _agent_model_for_backend,
    _agent_model_from_env,
    _build_aut_agent_cmd,
    _build_claude_code_agent_cmd,
    _build_codex_agent_cmd,
    _build_cursor_agent_cmd,
    _normalize_secret,
    _prepare_aut_config_for_runtime,
    run_agent_phase,
)


@pytest.fixture()
def aut_config(tmp_path: Path) -> Path:
    """Write a minimal AUT-style YAML config and return the path."""
    config = {
        "llms": {
            "agent": {
                "_type": "openai",
                "api_key": "not-used",
                "model_name": "aws-anthropic-claude-opus-4-5",
            }
        }
    }
    p = tmp_path / "agent.yml"
    with p.open("w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    return p


class TestIGWRouting:
    """Verify _prepare_aut_config_for_runtime injects IGW routing via inject_gateway_url."""

    def test_injects_igw_base_url(self, aut_config: Path, tmp_path: Path) -> None:
        result = _prepare_aut_config_for_runtime(aut_config, tmp_path)
        cfg = yaml.safe_load(result.read_text())
        expected = "http://localhost:8080/apis/inference-gateway/v2/workspaces/default/openai/-/v1"
        assert cfg["llms"]["agent"]["base_url"] == expected

    def test_preserves_entity_model_name(self, aut_config: Path, tmp_path: Path) -> None:
        result = _prepare_aut_config_for_runtime(aut_config, tmp_path)
        cfg = yaml.safe_load(result.read_text())
        assert cfg["llms"]["agent"]["model_name"] == "aws-anthropic-claude-opus-4-5"

    def test_overrides_model_name_with_nat_model(self, aut_config: Path, tmp_path: Path) -> None:
        result = _prepare_aut_config_for_runtime(aut_config, tmp_path, nat_model="custom-model")
        cfg = yaml.safe_load(result.read_text())
        assert cfg["llms"]["agent"]["model_name"] == "custom-model"

    def test_custom_workspace(self, aut_config: Path, tmp_path: Path) -> None:
        result = _prepare_aut_config_for_runtime(aut_config, tmp_path, workspace="staging")
        cfg = yaml.safe_load(result.read_text())
        assert "/workspaces/staging/" in cfg["llms"]["agent"]["base_url"]

    def test_preserves_explicit_base_url(self, tmp_path: Path) -> None:
        """inject_gateway_url uses setdefault -- explicit base_url is preserved."""
        config = {
            "llms": {
                "agent": {
                    "_type": "openai",
                    "api_key": "real-key",
                    "base_url": "http://my-custom-endpoint/v1",
                    "model_name": "my-model",
                }
            }
        }
        p = tmp_path / "explicit.yml"
        with p.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        result = _prepare_aut_config_for_runtime(p, tmp_path)
        cfg = yaml.safe_load(result.read_text())
        assert cfg["llms"]["agent"]["base_url"] == "http://my-custom-endpoint/v1"
        assert cfg["llms"]["agent"]["api_key"] == "real-key"

    def test_writes_rewritten_to_output_dir(self, aut_config: Path, tmp_path: Path) -> None:
        result = _prepare_aut_config_for_runtime(aut_config, tmp_path)
        assert result.parent == tmp_path
        assert result.name == "aut.runtime.yml"

    def test_custom_base_url_and_port(self, aut_config: Path, tmp_path: Path) -> None:
        result = _prepare_aut_config_for_runtime(
            aut_config,
            tmp_path,
            nmp_base_url="http://myhost:9090",
        )
        cfg = yaml.safe_load(result.read_text())
        assert cfg["llms"]["agent"]["base_url"].startswith("http://myhost:9090/")

    def test_trailing_slash_stripped(self, aut_config: Path, tmp_path: Path) -> None:
        result = _prepare_aut_config_for_runtime(
            aut_config,
            tmp_path,
            nmp_base_url="http://localhost:8080/",
        )
        cfg = yaml.safe_load(result.read_text())
        assert "//apis" not in cfg["llms"]["agent"]["base_url"]

    def test_non_openai_llm_not_injected(self, tmp_path: Path) -> None:
        """LLMs with _type != openai/nim are left untouched."""
        config = {
            "llms": {
                "agent": {
                    "_type": "huggingface",
                    "model_name": "some-model",
                }
            }
        }
        p = tmp_path / "hf.yml"
        with p.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        result = _prepare_aut_config_for_runtime(p, tmp_path)
        cfg = yaml.safe_load(result.read_text())
        assert "base_url" not in cfg["llms"]["agent"]


class TestAgentBackends:
    """Verify backend-specific command construction and metadata helpers."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, ""),
            ("", ""),
            ("  ", ""),
            ("null", ""),
            (" NULL ", ""),
            ("None", ""),
            (" none ", ""),
            ("actual-secret", "actual-secret"),
            (" actual-secret ", "actual-secret"),
        ],
    )
    def test_normalize_secret(self, value: str | None, expected: str) -> None:
        assert _normalize_secret(value) == expected

    def test_build_claude_code_agent_cmd_uses_unified_agent_model(self) -> None:
        cmd = _build_claude_code_agent_cmd("/tmp/instruction.md")
        script = cmd[2]

        assert cmd[:2] == ["bash", "-c"]
        assert "claude -p" in script
        assert "AGENT_MODEL" in script
        assert "CLAUDE_MODEL" not in script
        assert "--output-format json" in script

    def test_build_aut_agent_cmd_recreates_existing_agent_when_config_is_present(self) -> None:
        cmd = _build_aut_agent_cmd("/tmp/instruction.md")
        script = cmd[2]

        assert 'if [ -n "${EFFECTIVE_AUT_AGENT_CONFIG}" ]; then' in script
        assert 'nemo agents undeploy --agent "${AUT_AGENT_NAME}"' in script
        assert 'nemo agents delete "${AUT_AGENT_NAME}"' in script
        assert 'nemo agents create --name "${AUT_AGENT_NAME}" --agent-config "${EFFECTIVE_AUT_AGENT_CONFIG}"' in script

    def test_build_aut_agent_cmd_keeps_diagnostics_best_effort(self) -> None:
        cmd = _build_aut_agent_cmd("/tmp/instruction.md")
        script = cmd[2]

        assert "set +e" in script
        assert "cleanup_rc=$?" in script
        assert 'exit "$cleanup_rc"' in script
        assert ">/tmp/aut_deployments.list.json 2>&1" in script
        assert ">/logs/agent/aut_deployments.list.json" not in script
        assert "mkdir -p /logs/agent/nat_subprocess_logs 2>/dev/null || true" in script

    def test_build_aut_agent_cmd_has_valid_shell_syntax(self) -> None:
        script = _build_aut_agent_cmd("/tmp/instruction.md")[2]

        subprocess.run(["bash", "-n"], input=script, text=True, check=True)

    def test_build_codex_agent_cmd_runs_headlessly_with_artifacts(self) -> None:
        cmd = _build_codex_agent_cmd("/tmp/instruction.md")
        script = cmd[2]

        assert cmd[:2] == ["bash", "-c"]
        assert nat_runner.CODEX_AGENT_SCRIPT_TEMPLATE_PATH.is_file()
        assert "codex exec" in script
        assert "--sandbox read-only" in script
        assert "--output-schema /tmp/codex_output_schema.json" in script
        assert "--output-last-message /logs/agent/codex_structured_output.json" in script
        assert "codex_structured_prompt.md" in script
        assert "output_files" in script
        assert "final_message.txt" in script
        assert "--dangerously-bypass-approvals-and-sandbox" not in script
        assert "--output-last-message /logs/agent/final_message.txt" not in script
        assert "--json" in script
        assert "AGENT_MODEL" in script
        assert "CODEX_HOME" in script
        assert "/tmp/codex_host_auth.json" in script
        assert "CODEX_MODEL" not in script
        assert "/tmp/instruction.md" in script
        assert "@@CODEX_STRUCTURED_OUTPUT_SCHEMA@@" not in script
        assert "@@INSTRUCTION_CONTAINER@@" not in script

    def test_codex_agent_script_template_has_valid_shell_syntax(self) -> None:
        subprocess.run(["bash", "-n", str(nat_runner.CODEX_AGENT_SCRIPT_TEMPLATE_PATH)], check=True)

    def test_build_cursor_agent_cmd_runs_headlessly_with_artifacts(self) -> None:
        cmd = _build_cursor_agent_cmd("/tmp/instruction.md")
        script = cmd[2]

        assert cmd[:2] == ["bash", "-c"]
        assert "cursor-agent" in script
        assert "--print" in script
        assert "--output-format json" in script
        assert "--force" not in script
        assert "--sandbox disabled" in script
        assert "--workspace /app" in script
        assert "AGENT_MODEL" in script
        assert "CURSOR_MODEL" not in script
        assert "/tmp/instruction.md" in script

    @pytest.mark.parametrize(
        ("agent_backend", "expected"),
        [
            ("claude-code", "agent-model"),
            ("codex", "agent-model"),
            ("cursor-agent", "agent-model"),
            ("workflow", "agent-model"),
            ("aut", "agent-model"),
        ],
    )
    def test_agent_model_for_backend(self, agent_backend: str, expected: str) -> None:
        assert (
            _agent_model_for_backend(
                agent_backend=agent_backend,
                agent_model="agent-model",
            )
            == expected
        )

    def test_agent_model_for_backend_defaults_optional_direct_agent_models(self) -> None:
        assert (
            _agent_model_for_backend(
                agent_backend="codex",
                agent_model=None,
            )
            == "default"
        )
        assert (
            _agent_model_for_backend(
                agent_backend="cursor-agent",
                agent_model=None,
            )
            == "default"
        )
        assert (
            _agent_model_for_backend(
                agent_backend="claude-code",
                agent_model=None,
            )
            == "default"
        )
        assert (
            _agent_model_for_backend(
                agent_backend="aut",
                agent_model=None,
            )
            == "unknown"
        )

    def test_agent_model_from_env_prefers_unified_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("NAT_AGENT_MODEL", "unified")
        monkeypatch.setenv("CODEX_MODEL", "legacy-codex")

        assert _agent_model_from_env("codex") == "unified"

    def test_agent_model_from_env_reads_backend_legacy_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CURSOR_MODEL", "legacy-cursor")

        assert _agent_model_from_env("cursor-agent") == "legacy-cursor"

    def test_agent_model_from_env_reads_legacy_nat_model_for_platform_backends(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("NAT_MODEL", "legacy-nat")

        assert _agent_model_from_env("workflow") == "legacy-nat"

    def test_run_agent_phase_scopes_direct_agent_secrets(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        task_dir = tmp_path / "task"
        task_dir.mkdir()
        (task_dir / "instruction.md").write_text("Do the thing.")
        output_dir = tmp_path / "out"
        state_dir = tmp_path / "state"
        workspace_dir = tmp_path / "workspace"

        monkeypatch.setenv("OPENAI_API_KEY", " openai-secret ")
        monkeypatch.setenv("CURSOR_API_KEY", "cursor-secret")
        monkeypatch.setenv("INFERENCE_NVIDIA_API_KEY", "inference-secret")
        captured_env: dict[str, str] = {}

        def fake_docker_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess:
            env = kwargs["env"]
            assert isinstance(env, dict)
            captured_env.update(env)
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

        monkeypatch.setattr(nat_runner, "_docker_run", fake_docker_run)

        assert run_agent_phase(
            task_dir,
            "task-image",
            output_dir,
            nvidia_api_key="nvidia-secret",
            anthropic_api_key="anthropic-secret",
            anthropic_base_url="https://anthropic.example",
            nmp_base_url="http://localhost:8080",
            agent_model=None,
            codex_auth_json=None,
            timeout=10,
            agent_backend="codex",
            aut_agent_name="test-agent",
            aut_agent_config=None,
            aut_seed_providers=True,
            state_dir=state_dir,
            workspace_dir=workspace_dir,
        )

        assert captured_env["OPENAI_API_KEY"] == "openai-secret"
        assert captured_env["AGENTIC_USE_WORKSPACE_DIR"] == "/app/workspace"
        assert "CURSOR_API_KEY" not in captured_env
        assert "NVIDIA_API_KEY" not in captured_env
        assert "ANTHROPIC_API_KEY" not in captured_env
        assert "INFERENCE_NVIDIA_API_KEY" not in captured_env

    def test_run_agent_phase_mounts_explicit_codex_auth_read_only(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        codex_home = tmp_path / ".codex"
        codex_home.mkdir()
        codex_auth = codex_home / "auth.json"
        codex_auth.write_text("{}")

        task_dir = tmp_path / "task"
        task_dir.mkdir()
        (task_dir / "instruction.md").write_text("Do the thing.")
        output_dir = tmp_path / "out"
        state_dir = tmp_path / "state"
        workspace_dir = tmp_path / "workspace"
        captured_mounts: list[tuple[str, str]] = []

        def fake_docker_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess:
            mounts = kwargs["mounts"]
            assert isinstance(mounts, list)
            captured_mounts.extend(mounts)
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

        monkeypatch.setattr(nat_runner, "_docker_run", fake_docker_run)

        assert run_agent_phase(
            task_dir,
            "task-image",
            output_dir,
            nvidia_api_key="nvidia-secret",
            anthropic_api_key="anthropic-secret",
            anthropic_base_url="https://anthropic.example",
            nmp_base_url="http://localhost:8080",
            agent_model=None,
            codex_auth_json=codex_auth,
            timeout=10,
            agent_backend="codex",
            aut_agent_name="test-agent",
            aut_agent_config=None,
            aut_seed_providers=True,
            state_dir=state_dir,
            workspace_dir=workspace_dir,
        )

        assert (str(codex_auth), "/tmp/codex_host_auth.json:ro") in captured_mounts
        assert (str(workspace_dir), "/app/workspace") in captured_mounts
        assert (str(codex_home), "/tmp/codex_host_home") not in captured_mounts

    def test_run_agent_phase_normalizes_platform_agent_secrets(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        task_dir = tmp_path / "task"
        task_dir.mkdir()
        (task_dir / "instruction.md").write_text("Do the thing.")
        output_dir = tmp_path / "out"
        state_dir = tmp_path / "state"
        workspace_dir = tmp_path / "workspace"

        monkeypatch.setenv("OPENAI_API_KEY", "openai-secret")
        monkeypatch.setenv("CURSOR_API_KEY", "cursor-secret")
        monkeypatch.setenv("INFERENCE_NVIDIA_API_KEY", " none ")
        # Also neutralize the NVIDIA_INFERENCE_API_KEY alias so the test is
        # deterministic regardless of host env. nat_runner falls back to this
        # var when INFERENCE_NVIDIA_API_KEY is unset/null.
        monkeypatch.setenv("NVIDIA_INFERENCE_API_KEY", " none ")
        captured_env: dict[str, str] = {}

        def fake_docker_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess:
            env = kwargs["env"]
            assert isinstance(env, dict)
            captured_env.update(env)
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

        monkeypatch.setattr(nat_runner, "_docker_run", fake_docker_run)

        assert run_agent_phase(
            task_dir,
            "task-image",
            output_dir,
            nvidia_api_key=" nvidia-secret ",
            anthropic_api_key=" null ",
            anthropic_base_url="https://anthropic.example",
            nmp_base_url="http://localhost:8080",
            agent_model=None,
            codex_auth_json=None,
            timeout=10,
            agent_backend="aut",
            aut_agent_name="test-agent",
            aut_agent_config=None,
            aut_seed_providers=True,
            state_dir=state_dir,
            workspace_dir=workspace_dir,
        )

        assert captured_env["NVIDIA_API_KEY"] == "nvidia-secret"
        assert "ANTHROPIC_API_KEY" not in captured_env
        assert "OPENAI_API_KEY" not in captured_env
        assert "CURSOR_API_KEY" not in captured_env
        assert "INFERENCE_NVIDIA_API_KEY" not in captured_env


class TestAgentLogWorkflowErrors:
    def test_detects_workflow_error_json_payload(self) -> None:
        agent_log = """
intermediate_data: {"event": "tool_start"}
{"code":"workflow_error","message":"Error in react_agent workflow","details":"RuntimeError"}
"""

        assert _agent_log_has_workflow_error(agent_log)

    def test_ignores_successful_messages_payload(self) -> None:
        agent_log = '{"messages":[{"role":"assistant","content":"completed"}]}'

        assert not _agent_log_has_workflow_error(agent_log)


class TestAutValidation:
    """Verify that nat_runner.main() rejects AUT mode when required args are missing."""

    @pytest.fixture(autouse=True)
    def _fake_api_key(self, monkeypatch):
        monkeypatch.setenv("NVIDIA_API_KEY", "fake-key-for-test")

    def test_rejects_aut_without_agent_name(self, monkeypatch, tmp_path, capsys):
        config = tmp_path / "agent.yml"
        config.write_text("llms: {}\n")
        monkeypatch.setattr(
            "sys.argv",
            [
                "nat_runner.py",
                "workspace-basic-mcp",
                "--agent-backend",
                "aut",
                "--aut-agent-config",
                str(config),
            ],
        )
        monkeypatch.delenv("AUT_AGENT_NAME", raising=False)
        result = nat_runner.main()
        assert result == 1
        assert "requires --aut-agent-name" in capsys.readouterr().err

    def test_rejects_aut_without_agent_config(self, monkeypatch, capsys):
        monkeypatch.setattr(
            "sys.argv",
            [
                "nat_runner.py",
                "workspace-basic-mcp",
                "--agent-backend",
                "aut",
                "--aut-agent-name",
                "test-agent",
            ],
        )
        monkeypatch.delenv("AUT_AGENT_CONFIG", raising=False)
        result = nat_runner.main()
        assert result == 1
        assert "requires --aut-agent-config" in capsys.readouterr().err
