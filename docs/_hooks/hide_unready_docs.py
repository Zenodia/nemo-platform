# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Hide temporarily unavailable docs from MkDocs builds.

Configured by the `extra.hidden_docs` block in mkdocs.yml.
"""

from __future__ import annotations

import posixpath
import re
from collections.abc import Sequence
from fnmatch import fnmatchcase
from html import escape
from typing import Any


INLINE_LINK_RE = re.compile(r"(?<!!)\[([^\]\n]+)\]\(([^)\n]+)\)")
API_CHIP_RE = re.compile(
    r'^[ \t]*<button\b(?=[^>]*\bclass="api-chip\b[^"]*")(?=[^>]*\bdata-tag="(?P<tag>[^"]*)")[^>]*>[^<]+</button>[ \t]*\n?',
    re.MULTILINE,
)


def on_config(config: Any, **_: Any) -> Any:
    hidden_docs = _hidden_docs_config(config)
    if not hidden_docs:
        return config

    sections, path_patterns, _ = hidden_docs
    nav = config.get("nav")
    if nav:
        config["nav"] = _filter_nav(nav, sections, path_patterns)

    return config


def on_files(files: Any, config: Any, **_: Any) -> Any:
    hidden_docs = _hidden_docs_config(config)
    if not hidden_docs:
        return files

    _, path_patterns, _ = hidden_docs
    for file in list(files):
        src_path = _file_src_path(file)
        if src_path and _matches_hidden_path(src_path, path_patterns):
            files.remove(file)

    return files


def on_page_markdown(markdown: str, page: Any, config: Any, **_: Any) -> str:
    hidden_docs = _hidden_docs_config(config)
    if not hidden_docs:
        return markdown

    _, path_patterns, api_tags = hidden_docs
    page_src_path = _file_src_path(page.file)

    def replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2)
        target_path = _resolve_link_target(target, page_src_path)
        if target_path and _matches_hidden_path(target_path, path_patterns):
            return label
        return match.group(0)

    markdown = INLINE_LINK_RE.sub(replace_link, markdown)
    if page_src_path == "api/index.md":
        markdown = _filter_api_reference(markdown, api_tags)

    return markdown


def _hidden_docs_config(config: Any) -> tuple[frozenset[str], tuple[str, ...], frozenset[str]] | None:
    extra = config.get("extra", {})
    hidden_docs = extra.get("hidden_docs", {})
    if not isinstance(hidden_docs, dict) or not _is_enabled(hidden_docs.get("enabled")):
        return None

    sections_val = _hidden_docs_sequence(hidden_docs, "sections")
    paths_val = _hidden_docs_sequence(hidden_docs, "paths")
    api_tags_val = _hidden_docs_sequence(hidden_docs, "api_tags")

    sections = frozenset(str(section) for section in sections_val)
    path_patterns = tuple(_normalize_pattern(pattern) for pattern in paths_val if str(pattern).strip())
    api_tags = frozenset(str(tag) for tag in api_tags_val)
    if not sections and not path_patterns and not api_tags:
        return None

    return sections, path_patterns, api_tags


def _hidden_docs_sequence(hidden_docs: dict[str, Any], key: str) -> Sequence[Any]:
    value = hidden_docs.get(key, ())
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"extra.hidden_docs.{key} must be a sequence, not {type(value).__name__}")
    return value


def _is_enabled(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "off"}
    return bool(value)


def _filter_nav(nav: list[Any], sections: frozenset[str], path_patterns: tuple[str, ...]) -> list[Any]:
    filtered_items: list[Any] = []
    for item in nav:
        filtered_item = _filter_nav_item(item, sections, path_patterns)
        if filtered_item is not None:
            filtered_items.append(filtered_item)
    return filtered_items


def _filter_nav_item(item: Any, sections: frozenset[str], path_patterns: tuple[str, ...]) -> Any | None:
    if isinstance(item, str):
        return None if _matches_hidden_path(item, path_patterns) else item

    if not isinstance(item, dict):
        return item

    filtered_item: dict[str, Any] = {}
    for title, value in item.items():
        if title in sections:
            continue

        if isinstance(value, str):
            if not _matches_hidden_path(value, path_patterns):
                filtered_item[title] = value
        elif isinstance(value, list):
            filtered_children = _filter_nav(value, sections, path_patterns)
            if filtered_children:
                filtered_item[title] = filtered_children
        else:
            filtered_item[title] = value

    return filtered_item or None


def _matches_hidden_path(path: str, patterns: tuple[str, ...]) -> bool:
    normalized_path = _normalize_path(path)
    for pattern in patterns:
        if pattern.endswith("/**"):
            directory = pattern[:-3]
            if normalized_path == directory or normalized_path.startswith(f"{directory}/"):
                return True

        if fnmatchcase(normalized_path, pattern):
            return True

    return False


def _filter_api_reference(markdown: str, api_tags: frozenset[str]) -> str:
    if not api_tags:
        return markdown

    markdown = API_CHIP_RE.sub(
        lambda match: "" if match.group("tag") in api_tags else match.group(0),
        markdown,
    )

    if "data-hidden-tags=" in markdown:
        return markdown

    hidden_tags = ",".join(escape(tag, quote=True) for tag in sorted(api_tags))
    return markdown.replace(
        '<div class="api-filter-chips">',
        f'<div class="api-filter-chips" data-hidden-tags="{hidden_tags}">',
        1,
    )


def _resolve_link_target(target: str, page_src_path: str) -> str | None:
    target_path = target.strip()
    if not target_path:
        return None

    if target_path.startswith("<") and ">" in target_path:
        target_path = target_path[1 : target_path.index(">")]
    else:
        target_path = target_path.split(maxsplit=1)[0]

    if (
        not target_path
        or target_path.startswith("#")
        or target_path.startswith("//")
        or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target_path)
    ):
        return None

    target_path = target_path.split("#", 1)[0].split("?", 1)[0]
    if not target_path:
        return None

    if target_path.startswith("/"):
        return _normalize_path(target_path)

    page_directory = posixpath.dirname(_normalize_path(page_src_path))
    return _normalize_path(posixpath.join(page_directory, target_path))


def _file_src_path(file: Any) -> str:
    return _normalize_path(getattr(file, "src_uri", "") or getattr(file, "src_path", ""))


def _normalize_pattern(pattern: Any) -> str:
    return _normalize_path(str(pattern).strip())


def _normalize_path(path: str) -> str:
    return posixpath.normpath(path.strip().replace("\\", "/")).lstrip("./")
