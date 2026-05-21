# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for ``nemo agents delete``, ``undeploy``, and ``deployments delete`` confirmation flags.

Verifies:
- Interactive confirmation prompts when ``--yes`` is not set
- Abort on user decline
- ``--yes`` / ``-y`` skips the prompt
- ``--all`` works as an alias for ``--agent`` on ``undeploy``
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from nemo_agents_plugin.cli import AgentsCLI
from typer.testing import CliRunner

runner = CliRunner()

_PATCH_PREFIX = "nemo_agents_plugin.cli"


@pytest.fixture
def app():
    """Build the ``nemo agents`` Typer app."""
    return AgentsCLI().get_cli()


# ---------------------------------------------------------------------------
# nemo agents delete
# ---------------------------------------------------------------------------


class TestDeleteConfirmation:
    def test_delete_prompts_when_no_yes_flag(self, app) -> None:
        """Without --yes, the user is prompted; answering 'y' proceeds."""
        with patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete:
            result = runner.invoke(app, ["delete", "my-agent"], input="y\n")

        assert result.exit_code == 0, result.output
        mock_delete.assert_called_once()
        assert "deleted" in result.output.lower()

    def test_delete_aborts_when_user_declines(self, app) -> None:
        """Without --yes, answering 'n' aborts without calling the API."""
        with patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete:
            result = runner.invoke(app, ["delete", "my-agent"], input="n\n")

        assert result.exit_code != 0
        mock_delete.assert_not_called()

    @pytest.mark.parametrize("flag", ["--yes", "-y"])
    def test_delete_skips_prompt_with_yes_flag(self, app, flag: str) -> None:
        """--yes and -y both skip the confirmation prompt."""
        with patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete:
            result = runner.invoke(app, ["delete", "my-agent", flag])

        assert result.exit_code == 0, result.output
        mock_delete.assert_called_once()
        assert "deleted" in result.output.lower()


# ---------------------------------------------------------------------------
# nemo agents undeploy
# ---------------------------------------------------------------------------


def _mock_deployments_response(deployments: list[dict]) -> dict:
    """Build a fake paginated response for GET /deployments."""
    return {"data": deployments}


class TestUndeployConfirmation:
    def test_undeploy_single_prompts_confirmation(self, app) -> None:
        """Undeploying a single deployment prompts for confirmation."""
        with patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete:
            result = runner.invoke(app, ["undeploy", "dep-1"], input="y\n")

        assert result.exit_code == 0, result.output
        mock_delete.assert_called_once()

    def test_undeploy_single_aborts_on_decline(self, app) -> None:
        """Declining the prompt does not call the API."""
        with patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete:
            result = runner.invoke(app, ["undeploy", "dep-1"], input="n\n")

        assert result.exit_code != 0
        mock_delete.assert_not_called()

    def test_undeploy_single_yes_skips_prompt(self, app) -> None:
        """--yes skips the confirmation for single deployment undeploy."""
        with patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete:
            result = runner.invoke(app, ["undeploy", "dep-1", "--yes"])

        assert result.exit_code == 0, result.output
        mock_delete.assert_called_once()

    def test_undeploy_by_agent_prompts_with_count(self, app) -> None:
        """Undeploying by --agent lists deployments, shows count in prompt, and deletes on 'y'."""
        deps = _mock_deployments_response(
            [
                {"name": "dep-1", "agent": "my-agent"},
                {"name": "dep-2", "agent": "my-agent"},
            ]
        )
        with (
            patch(f"{_PATCH_PREFIX}._api_get", return_value=deps),
            patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete,
        ):
            result = runner.invoke(app, ["undeploy", "--agent", "my-agent"], input="y\n")

        assert result.exit_code == 0, result.output
        assert mock_delete.call_count == 2

    def test_undeploy_by_agent_aborts_on_decline(self, app) -> None:
        """Declining the prompt after listing does not delete anything."""
        deps = _mock_deployments_response(
            [
                {"name": "dep-1", "agent": "my-agent"},
                {"name": "dep-2", "agent": "my-agent"},
            ]
        )
        with (
            patch(f"{_PATCH_PREFIX}._api_get", return_value=deps),
            patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete,
        ):
            result = runner.invoke(app, ["undeploy", "--agent", "my-agent"], input="n\n")

        assert result.exit_code != 0
        mock_delete.assert_not_called()

    def test_undeploy_all_flag_works_as_agent_alias(self, app) -> None:
        """--all is an alias for --agent on undeploy."""
        deps = _mock_deployments_response(
            [
                {"name": "dep-1", "agent": "my-agent"},
            ]
        )
        with (
            patch(f"{_PATCH_PREFIX}._api_get", return_value=deps),
            patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete,
        ):
            result = runner.invoke(app, ["undeploy", "--all", "my-agent", "--yes"])

        assert result.exit_code == 0, result.output
        mock_delete.assert_called_once()


# ---------------------------------------------------------------------------
# nemo agents deployments delete
# ---------------------------------------------------------------------------


class TestDeploymentsDeleteConfirmation:
    def test_deployments_delete_prompts_without_yes(self, app) -> None:
        """deployments delete prompts for confirmation."""
        with patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete:
            result = runner.invoke(app, ["deployments", "delete", "dep-1"], input="y\n")

        assert result.exit_code == 0, result.output
        mock_delete.assert_called_once()

    def test_deployments_delete_aborts_on_decline(self, app) -> None:
        """Declining aborts without calling the API."""
        with patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete:
            result = runner.invoke(app, ["deployments", "delete", "dep-1"], input="n\n")

        assert result.exit_code != 0
        mock_delete.assert_not_called()

    def test_deployments_delete_skips_with_yes(self, app) -> None:
        """--yes skips the confirmation prompt."""
        with patch(f"{_PATCH_PREFIX}._api_delete") as mock_delete:
            result = runner.invoke(app, ["deployments", "delete", "dep-1", "--yes"])

        assert result.exit_code == 0, result.output
        mock_delete.assert_called_once()
