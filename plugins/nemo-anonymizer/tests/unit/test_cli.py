# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from nemo_anonymizer_plugin import cli as cli_module
from nemo_anonymizer_plugin.cli import AnonymizerCLI
from typer.testing import CliRunner


def _write_config(path: Path) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "replace": {
                    "kind": "redact",
                    "format_template": "[REDACTED_{label}]",
                }
            }
        )
    )


def test_cli_only_registers_manual_validate_command() -> None:
    result = CliRunner().invoke(AnonymizerCLI().get_cli(), ["--help"])

    assert result.exit_code == 0, result.output
    assert "validate" in result.output
    assert "preview-local" not in result.output
    assert "run-local" not in result.output


def test_validate_command_runs_library_validation(tmp_path: Path, monkeypatch) -> None:
    captured: dict[str, Any] = {}

    class FakeAnonymizer:
        def validate_config(self, config: object) -> None:
            captured["config"] = config

    def fake_make_local_anonymizer(*, model_configs: str | Path | None, artifact_path: Path | None = None):
        captured["model_configs"] = model_configs
        captured["artifact_path"] = artifact_path
        return FakeAnonymizer()

    monkeypatch.setattr(cli_module, "_make_local_anonymizer", fake_make_local_anonymizer)

    config = tmp_path / "config.yaml"
    model_configs = tmp_path / "models.yaml"
    _write_config(config)
    model_configs.write_text("model_configs: []\n")

    result = CliRunner().invoke(
        AnonymizerCLI().get_cli(),
        [
            "validate",
            "--config",
            str(config),
            "--model-configs",
            str(model_configs),
        ],
    )

    assert result.exit_code == 0, result.output
    assert captured["model_configs"] == str(model_configs)
    assert captured["artifact_path"] is None
    assert "Config is valid." in result.output
