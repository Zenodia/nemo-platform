# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""nemo docs command - read NeMo Platform documentation from the CLI."""

from __future__ import annotations

import os
import posixpath
import sys
from collections.abc import Sequence
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Annotated

import typer
import yaml


class _MkDocsConfigLoader(yaml.SafeLoader):
    """YAML loader that tolerates MkDocs-specific tags."""


def _construct_env(loader: _MkDocsConfigLoader, node: yaml.Node) -> object:
    if isinstance(node, yaml.SequenceNode):
        values = loader.construct_sequence(node)
        if len(values) == 1:
            env_names = values
            default = None
        else:
            env_names = values[:-1]
            default = values[-1] if values else None
        for env_name in env_names:
            env_value = os.environ.get(str(env_name))
            if env_value is not None:
                return env_value
        return default

    env_name = loader.construct_scalar(node)
    return os.environ.get(env_name, "")


def _construct_unknown(loader: _MkDocsConfigLoader, _tag_suffix: str, node: yaml.Node) -> object:
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_scalar(node)


_MkDocsConfigLoader.add_constructor("!ENV", _construct_env)
_MkDocsConfigLoader.add_multi_constructor("", _construct_unknown)


def _find_docs_root(module_file: Path | None = None) -> Path | None:
    """Find the docs/ directory, checking env var then the CLI source tree."""
    env_root = os.environ.get("NMP_DOCS_ROOT")
    if env_root:
        p = Path(env_root)
        if p.is_dir():
            return p.resolve()

    module_path = Path(__file__) if module_file is None else module_file
    parents = module_path.resolve().parents

    for parent in parents:
        docs_dir = parent / "docs"
        mkdocs_config = parent / "mkdocs.yml"
        if mkdocs_config.is_file() and docs_dir.is_dir():
            return docs_dir.resolve()

    for parent in parents:
        docs_dir = parent / "docs"
        if docs_dir.is_dir() and (docs_dir / "index.md").is_file():
            return docs_dir.resolve()

    return None


def _normalize_path(path: str) -> str:
    return posixpath.normpath(path.strip().replace("\\", "/")).lstrip("./")


def _normalize_pattern(pattern: object) -> str:
    raw_pattern = str(pattern).strip().replace("\\", "/")
    is_directory_pattern = raw_pattern.endswith("/") and not raw_pattern.endswith("/**")
    normalized = _normalize_path(raw_pattern)
    if is_directory_pattern and not normalized.endswith("/"):
        return f"{normalized}/"
    return normalized


def _is_enabled(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "off"}
    return bool(value)


def _load_mkdocs_config(docs_root: Path) -> dict[str, object]:
    config_path = docs_root.parent / "mkdocs.yml"
    if not config_path.is_file():
        return {}

    try:
        loaded = yaml.load(config_path.read_text(encoding="utf-8"), Loader=_MkDocsConfigLoader)
    except (OSError, yaml.YAMLError):
        return {}

    return loaded if isinstance(loaded, dict) else {}


def _sequence_value(value: object) -> Sequence[object]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        return ()
    return value


def _exclude_patterns(config: dict[str, object]) -> tuple[str, ...]:
    exclude_docs = config.get("exclude_docs", "")
    if isinstance(exclude_docs, str):
        return tuple(
            _normalize_pattern(line)
            for line in exclude_docs.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )

    return tuple(_normalize_pattern(pattern) for pattern in _sequence_value(exclude_docs) if str(pattern).strip())


def _hidden_doc_patterns(config: dict[str, object]) -> tuple[str, ...]:
    extra = config.get("extra", {})
    if not isinstance(extra, dict):
        return ()

    hidden_docs = extra.get("hidden_docs", {})
    if not isinstance(hidden_docs, dict) or not _is_enabled(hidden_docs.get("enabled")):
        return ()

    return tuple(
        _normalize_pattern(pattern) for pattern in _sequence_value(hidden_docs.get("paths", ())) if str(pattern).strip()
    )


def _matches_pattern(path: str, pattern: str) -> bool:
    if pattern.endswith("/"):
        directory = pattern.rstrip("/")
        return path == directory or path.startswith(f"{directory}/")

    if pattern.endswith("/**"):
        directory = pattern[:-3]
        return path == directory or path.startswith(f"{directory}/")

    return fnmatchcase(path, pattern)


def _matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(_matches_pattern(path, pattern) for pattern in patterns)


def _is_visible_doc(rel_path: Path, exclude_patterns: tuple[str, ...], hidden_patterns: tuple[str, ...]) -> bool:
    if any(part.startswith("_") or part.startswith(".") for part in rel_path.parts):
        return False

    posix_rel_path = rel_path.as_posix()
    return not _matches_any(posix_rel_path, exclude_patterns) and not _matches_any(posix_rel_path, hidden_patterns)


def _list_docs(docs_root: Path) -> list[str]:
    """List doc topics that match the rendered MkDocs site."""
    config = _load_mkdocs_config(docs_root)
    exclude = _exclude_patterns(config)
    hidden = _hidden_doc_patterns(config)

    paths = []
    for md_file in sorted(docs_root.rglob("*.md")):
        rel = md_file.relative_to(docs_root)
        if not _is_visible_doc(rel, exclude, hidden):
            continue
        paths.append(rel.with_suffix("").as_posix())
    return paths


def _topic_from_user_path(path: str) -> str | None:
    raw_path = path.strip().replace("\\", "/")
    if not raw_path or raw_path.startswith("/"):
        return None

    normalized = posixpath.normpath(raw_path)
    if normalized in {".", ".."} or normalized.startswith("../"):
        return None

    topic = normalized.removeprefix("./")
    if topic.endswith(".md"):
        topic = topic[:-3]

    return topic or None


def _resolve_doc_path(docs_root: Path, path: str) -> Path | None:
    topic = _topic_from_user_path(path)
    if topic is None:
        return None

    topics = set(_list_docs(docs_root))
    if topic not in topics:
        return None

    return (docs_root / f"{topic}.md").resolve()


def docs_command(
    path: Annotated[
        str | None,
        typer.Argument(
            help="Path to a doc topic (e.g., get-started/setup). Omit to see available topics.",
        ),
    ] = None,
    list_topics: Annotated[
        bool,
        typer.Option(
            "--list",
            "-l",
            help="List available documentation topics.",
        ),
    ] = False,
) -> None:
    """Read NeMo Platform documentation.

    Examples:
    nemo docs get-started/setup
    nemo docs --list
    nemo docs cli/configuration
    """
    docs_root = _find_docs_root()
    if docs_root is None:
        typer.echo(
            "Error: Could not find docs directory. Set NMP_DOCS_ROOT environment variable to the docs/ path.",
            err=True,
        )
        raise typer.Exit(code=1)

    if list_topics or path is None:
        topics = _list_docs(docs_root)
        if not topics:
            typer.echo("No documentation found.", err=True)
            raise typer.Exit(code=1)
        typer.echo("Available documentation topics:\n")
        for topic in topics:
            typer.echo(f"  {topic}")
        typer.echo("\nUsage: nemo docs <topic>")
        raise typer.Exit()

    doc_path = _resolve_doc_path(docs_root, path)
    if doc_path is None:
        if _topic_from_user_path(path) is None:
            typer.echo(f"Error: Invalid path: {path}", err=True)
            raise typer.Exit(code=1)

        typer.echo(f"Error: Documentation not found: {path}", err=True)
        stem = Path(path).stem
        matches = [t for t in _list_docs(docs_root) if stem in t]
        if matches:
            typer.echo("\nDid you mean:", err=True)
            for m in matches[:5]:
                typer.echo(f"  nemo docs {m}", err=True)
        else:
            typer.echo("Run `nemo docs --list` to see available topics.", err=True)
        raise typer.Exit(code=1)

    try:
        doc_path.relative_to(docs_root.resolve())
    except ValueError:
        typer.echo(f"Error: Invalid path: {path}", err=True)
        raise typer.Exit(code=1) from None

    content = doc_path.read_text(encoding="utf-8")
    sys.stdout.write(content)
