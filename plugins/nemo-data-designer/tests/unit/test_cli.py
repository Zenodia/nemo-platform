# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
import typer
from data_designer_nemo.nemotron_personas import WORKSPACE, get_resource_name_for_locale
from nemo_data_designer_plugin.cli import personas as personas_module
from nemo_data_designer_plugin.cli.main import DataDesignerCLI
from nemo_data_designer_plugin.functions.preview import PreviewFunction
from nemo_data_designer_plugin.jobs.create import CreateJob
from nemo_platform import NeMoPlatform
from nemo_platform.types.files import NGCStorageConfig
from nemo_platform_plugin.commands import add_function_commands, add_job_commands
from nmp.core.files.service import FilesService
from nmp.core.secrets.service import SecretsService
from nmp.testing import create_test_client
from typer.testing import CliRunner


@pytest.fixture
def mock_ngc_client() -> Generator[dict[str, Mock]]:
    with (
        patch("nmp.core.files.app.backends.ngc.Client") as mock_client_cls,
        patch("nmp.core.files.app.backends.ngc.ResourceAPI") as mock_resource_api_cls,
    ):
        mock_client = Mock()
        mock_resource_api = Mock()

        mock_client_cls.return_value = mock_client
        mock_resource_api_cls.return_value = mock_resource_api

        yield {
            "client": mock_client,
            "resource_api": mock_resource_api,
        }


@pytest.fixture
def sdk(monkeypatch: pytest.MonkeyPatch, mock_ngc_client: dict[str, Mock]) -> Generator[NeMoPlatform]:
    with create_test_client(
        FilesService,
        SecretsService,
        client_type=NeMoPlatform,
    ) as sdk:
        monkeypatch.setenv("NGC_API_KEY", "nvapi-abc123")
        yield sdk
        monkeypatch.delenv("NGC_API_KEY")


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def app() -> typer.Typer:
    cli = DataDesignerCLI()
    typer_app = cli.get_cli()
    add_function_commands(typer_app, {"preview": PreviewFunction}, cli=cli)
    add_job_commands(typer_app, {"create": CreateJob}, cli=cli)
    return typer_app


@pytest.fixture
def cli_sdk(monkeypatch: pytest.MonkeyPatch, sdk: NeMoPlatform) -> NeMoPlatform:
    monkeypatch.setattr(personas_module, "NeMoPlatform", lambda: sdk)
    return sdk


def test_make_fileset_creates_requested_locale_with_existing_secret(
    runner: CliRunner, app: typer.Typer, cli_sdk: NeMoPlatform
) -> None:
    result = runner.invoke(
        app,
        [
            "personas",
            "make-fileset",
            "--locale",
            "en_US",
            "--api-key-secret",
            "system/ngc-api-key",
        ],
    )

    assert result.exit_code == 0, result.output
    filesets = cli_sdk.files.filesets.list(workspace=WORKSPACE)
    assert [fileset.name for fileset in filesets.data] == [get_resource_name_for_locale("en_US")]

    fileset = cli_sdk.files.filesets.retrieve(name=get_resource_name_for_locale("en_US"), workspace=WORKSPACE)
    assert isinstance(fileset.storage, NGCStorageConfig)
    assert fileset.storage.api_key_secret == "system/ngc-api-key"


def test_make_fileset_creates_secret_from_env_then_fileset(
    monkeypatch: pytest.MonkeyPatch, runner: CliRunner, app: typer.Typer, cli_sdk: NeMoPlatform
) -> None:
    monkeypatch.setenv("MY_NGC_API_KEY", "nvapi-from-env")

    result = runner.invoke(
        app,
        [
            "personas",
            "make-fileset",
            "--locale",
            "en_US",
            "--api-key-secret",
            "system/my-ngc-key",
            "--api-key-env-var",
            "MY_NGC_API_KEY",
        ],
    )

    assert result.exit_code == 0, result.output
    secret = cli_sdk.secrets.access("my-ngc-key", workspace="system")
    assert secret.value == "nvapi-from-env"

    fileset = cli_sdk.files.filesets.retrieve(name=get_resource_name_for_locale("en_US"), workspace=WORKSPACE)
    assert isinstance(fileset.storage, NGCStorageConfig)
    assert fileset.storage.api_key_secret == "system/my-ngc-key"


def test_make_fileset_missing_env_var_is_clear(runner: CliRunner, app: typer.Typer) -> None:
    result = runner.invoke(
        app,
        [
            "personas",
            "make-fileset",
            "--locale",
            "en_US",
            "--api-key-secret",
            "system/my-ngc-key",
            "--api-key-env-var",
            "MISSING_NGC_API_KEY",
        ],
    )

    assert result.exit_code != 0
    assert "MISSING_NGC_API_KEY" in result.output
    assert "not set or is empty" in result.output


def test_make_fileset_unknown_locale_is_clear(runner: CliRunner, app: typer.Typer) -> None:
    result = runner.invoke(
        app,
        [
            "personas",
            "make-fileset",
            "--locale",
            "de_DE",
            "--api-key-secret",
            "system/ngc-api-key",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value for '--locale'" in result.output
    assert "de_DE" in result.output


def test_make_fileset_bare_secret_name_is_clear(runner: CliRunner, app: typer.Typer) -> None:
    result = runner.invoke(
        app,
        [
            "personas",
            "make-fileset",
            "--locale",
            "en_US",
            "--api-key-secret",
            "ngc-api-key",
        ],
    )

    assert result.exit_code != 0
    assert "WORKSPACE/NAME" in result.output


def test_make_fileset_create_secret_conflict_does_not_create_fileset(
    monkeypatch: pytest.MonkeyPatch, runner: CliRunner, app: typer.Typer, cli_sdk: NeMoPlatform
) -> None:
    cli_sdk.secrets.create(workspace="system", name="my-ngc-key", value="nvapi-existing")
    monkeypatch.setenv("MY_NGC_API_KEY", "nvapi-from-env")

    result = runner.invoke(
        app,
        [
            "personas",
            "make-fileset",
            "--locale",
            "en_US",
            "--api-key-secret",
            "system/my-ngc-key",
            "--api-key-env-var",
            "MY_NGC_API_KEY",
        ],
    )

    assert result.exit_code == 1
    assert "already exists" in result.output
    filesets = cli_sdk.files.filesets.list(workspace=WORKSPACE)
    assert filesets.data == []


def test_nemotron_personas_download_is_wired(runner: CliRunner, app: typer.Typer) -> None:
    result = runner.invoke(app, ["personas", "download", "--help"])

    assert result.exit_code == 0, result.output
    assert "Download Nemotron-Personas" in result.output
    assert "nemo data-designer personas download --list" in result.output
    assert "data-designer download personas" not in result.output


@pytest.mark.parametrize("verb", ["run", "submit"])
def test_preview_exposes_save_results_flags(runner: CliRunner, app: typer.Typer, verb: str) -> None:
    result = runner.invoke(app, ["preview", verb, "--help"])

    assert result.exit_code == 0, result.output
    assert "--save-results" in result.output
    assert "--artifact-path" in result.output
    assert "--non-interactive" in result.output
