# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import typer

# from nemo_platform_ext.cli.commands.api.customization.jobs import create_jobs as create_customization_job
from nemo_platform_ext.cli.commands.api.inference.deployments import create_deployments
from nemo_platform_ext.cli.commands.api.safe_synthesizer.jobs import create_jobs as create_safe_synthesizer_job


def _ctx(client: object) -> SimpleNamespace:
    state = MagicMock()
    state.agent_mode = False
    state.get_client.return_value = client
    state.get_output_format.return_value = None
    state.get_no_truncate.return_value = False
    state.get_timestamp_format.return_value = None
    return SimpleNamespace(obj=state)


# def test_customization_job_create_waits_for_created_job() -> None:
#     jobs = MagicMock()
#     jobs.create.return_value = SimpleNamespace(name="created-job")
#     client = SimpleNamespace(customization=SimpleNamespace(jobs=jobs))
#     ctx = _ctx(client)

#     with (
#         patch(
#             "nemo_platform_ext.cli.commands.api.customization.jobs.handle_code_generation",
#             return_value=False,
#         ) as handle_code_generation,
#         patch("nemo_platform_ext.cli.commands.api.customization.jobs.format_output"),
#         patch(
#             "nemo_platform_ext.cli.commands.api.customization.jobs.wait_for_platform_job",
#             return_value=True,
#         ) as wait_for_platform_job,
#     ):
#         create_customization_job(
#             ctx,
#             name="input-job",
#             workspace="test-workspace",
#             spec='{"training_type": "sft"}',
#             wait=True,
#             timeout=42,
#             poll_interval=7,
#         )

#     handle_code_generation.assert_called_once_with(
#         ["customization", "jobs"],
#         "create",
#         {"workspace": "test-workspace", "spec": {"training_type": "sft"}, "name": "input-job"},
#         None,
#         ctx.obj,
#         wait_config={"type": "platform_job", "resource_label": "customization job"},
#         wait_options={"timeout": 42, "poll_interval": 7},
#     )
#     jobs.create.assert_called_once_with(
#         workspace="test-workspace",
#         spec={"training_type": "sft"},
#         name="input-job",
#     )
#     wait_for_platform_job.assert_called_once_with(
#         jobs,
#         "created-job",
#         workspace="test-workspace",
#         resource_label="customization job",
#         timeout=42,
#         poll_interval=7,
#     )


def test_safe_synthesizer_job_create_uses_input_name_for_wait_when_response_has_no_name() -> None:
    jobs = MagicMock()
    jobs.create.return_value = SimpleNamespace()
    client = SimpleNamespace(safe_synthesizer=SimpleNamespace(jobs=jobs))

    with (
        patch("nemo_platform_ext.cli.commands.api.safe_synthesizer.jobs.handle_code_generation", return_value=False),
        patch("nemo_platform_ext.cli.commands.api.safe_synthesizer.jobs.format_output"),
        patch(
            "nemo_platform_ext.cli.commands.api.safe_synthesizer.jobs.wait_for_platform_job",
            return_value=True,
        ) as wait_for_platform_job,
    ):
        create_safe_synthesizer_job(
            _ctx(client),
            name="safe-job",
            workspace="test-workspace",
            spec='{"source": "dataset"}',
            wait=True,
            timeout=60,
            poll_interval=5,
        )

    wait_for_platform_job.assert_called_once_with(
        jobs,
        "safe-job",
        workspace="test-workspace",
        resource_label="safe-synthesizer job",
        timeout=60,
        poll_interval=5,
    )


def test_inference_deployment_create_exits_when_wait_fails() -> None:
    deployments = MagicMock()
    deployments.create.return_value = SimpleNamespace(name="deployment-a")
    client = SimpleNamespace(inference=SimpleNamespace(deployments=deployments))

    with (
        patch("nemo_platform_ext.cli.commands.api.inference.deployments.handle_code_generation", return_value=False),
        patch("nemo_platform_ext.cli.commands.api.inference.deployments.format_output"),
        patch(
            "nemo_platform_ext.cli.commands.api.inference.deployments.wait_for_inference_deployment",
            return_value=False,
        ) as wait_for_inference_deployment,
        pytest.raises(typer.Exit) as exc_info,
    ):
        create_deployments(
            _ctx(client),
            name="deployment-a",
            workspace="test-workspace",
            config="deployment-config",
            wait=True,
            timeout=90,
            poll_interval=10,
        )

    assert exc_info.value.exit_code == 1
    wait_for_inference_deployment.assert_called_once_with(
        client,
        "deployment-a",
        workspace="test-workspace",
        timeout=90,
        poll_interval=10,
    )
