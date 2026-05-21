# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""CLI surface for the evaluator plugin scaffold."""

from __future__ import annotations

import json
from typing import ClassVar

import typer
from nemo_platform_plugin.cli import NemoCLI


class EvaluatorPluginCLI(NemoCLI):
    """CLI surface for the evaluator plugin scaffold."""

    name: ClassVar[str] = "evaluator"
    description: ClassVar[str] = "Evaluator plugin commands."

    def get_cli(self) -> typer.Typer:
        app = typer.Typer(
            name=self.name,
            help=self.description,
            no_args_is_help=True,
        )

        @app.command("info")
        def info() -> None:
            """Print the current plugin status."""
            typer.echo(
                json.dumps(
                    {
                        "plugin": self.name,
                        "status": "ready",
                        "service": "/apis/evaluator/v1/healthz",
                        "jobs": ["evaluator.evaluate"],
                        "sdk": "nemo_evaluator_sdk.Evaluator",
                    },
                    indent=2,
                )
            )

        return app
