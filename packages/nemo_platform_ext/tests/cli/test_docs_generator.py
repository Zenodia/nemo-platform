# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.util
from pathlib import Path

import typer
from nemo_platform_ext.cli.core.lazy_load import ManifestBackedNmpGroup, attach_lazy_entries
from nemo_platform_ext.cli.manifest import TopLevelEntry


def _load_docs_generator():
    for parent in Path(__file__).resolve().parents:
        docs_generator_path = parent / "packages" / "nemo_platform_ext" / "scripts" / "docs_generator.py"
        if docs_generator_path.exists():
            spec = importlib.util.spec_from_file_location("nemo_platform_ext_docs_generator", docs_generator_path)
            if spec is None or spec.loader is None:
                break
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise RuntimeError("Could not locate docs_generator.py")


_docs_generator = _load_docs_generator()
generate_docs = _docs_generator.generate_docs
generate_index_snippet = _docs_generator.generate_index_snippet


def test_index_snippet_skips_hidden_lazy_commands_without_loading():
    docs_app = typer.Typer(cls=ManifestBackedNmpGroup)

    @docs_app.callback()
    def main() -> None:
        """Test CLI."""

    @docs_app.command(rich_help_panel="Setup")
    def visible() -> None:
        """Visible command."""

    attach_lazy_entries(
        main,
        (
            TopLevelEntry(
                import_path="unused_docs_generator_test.module:visible",
                help="Manifest visible command help.",
                name="visible",
                panel="Setup",
                kind="command",
            ),
            TopLevelEntry(
                import_path="missing_docs_generator_test.module:app",
                help="Hidden command.",
                name="hidden-command",
                panel="Setup",
                kind="group",
                hidden=True,
            ),
        ),
    )

    snippet = generate_index_snippet(docs_app, name="nemo")
    reference = generate_docs(docs_app, name="nemo")

    assert "`visible`" in snippet
    assert "Manifest visible command help." in reference
    assert "Visible command." not in reference
    assert "hidden-command" not in snippet
    assert "Hidden command." not in snippet
    assert "* `--help, -h`: Show this message and exit." in reference
