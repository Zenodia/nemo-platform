# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Read and normalize captured agent artifacts."""

import json
from pathlib import Path
from typing import Any, Self

from pydantic import BaseModel, ConfigDict


class FinalAnswer(BaseModel):
    """Normalized final-answer extraction result."""

    model_config = ConfigDict(extra="forbid")

    extracted: bool
    text: str = ""
    source: str | None = None


class AgentArtifacts(BaseModel):
    """Captured files emitted by an agent run."""

    model_config = ConfigDict(extra="forbid")

    agent_log_dir: Path
    workspace_dir: Path | None = None
    final_answer: FinalAnswer
    raw_text: str = ""
    atif_trajectory_path: Path | None = None

    @classmethod
    def from_dir(cls, agent_log_dir: str | Path, *, workspace_dir: str | Path | None = None) -> Self:
        """Load known agent artifacts from a mounted ``/logs/agent`` directory."""
        root = Path(agent_log_dir)
        workspace = Path(workspace_dir) if workspace_dir is not None else None
        final_answer = _read_final_answer(root)
        raw_text = _read_raw_text(root)
        atif_trajectory_path = _find_atif_trajectory(root)
        return cls(
            agent_log_dir=root,
            workspace_dir=workspace,
            final_answer=final_answer,
            raw_text=raw_text,
            atif_trajectory_path=atif_trajectory_path,
        )

    def workspace_artifact(self, relative_path: str | Path) -> Path | None:
        """Return a workspace artifact path when it stays inside the workspace."""
        if self.workspace_dir is None:
            return None
        candidate = self.workspace_dir / relative_path
        try:
            candidate.resolve().relative_to(self.workspace_dir.resolve())
        except ValueError:
            return None
        return candidate


def _read_final_answer(root: Path) -> FinalAnswer:
    structured_path = root / "final_message.json"
    if structured_path.is_file():
        extracted = _final_answer_from_json_text(structured_path.read_text(encoding="utf-8", errors="replace"))
        if extracted.extracted:
            return FinalAnswer(extracted=True, text=extracted.text, source=f"{structured_path.name}:{extracted.source}")
        return FinalAnswer(extracted=False, source=structured_path.name)

    text_path = root / "final_message.txt"
    if text_path.is_file():
        text = text_path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            return FinalAnswer(extracted=False, source=text_path.name)
        parsed = _final_answer_from_json_text(text)
        if parsed.extracted:
            return FinalAnswer(extracted=True, text=parsed.text, source=f"{text_path.name}:{parsed.source}")
        if _looks_like_json(text):
            return FinalAnswer(extracted=False, source=text_path.name)
        return FinalAnswer(extracted=True, text=text, source=text_path.name)

    for name in ("nat_agent.log", "stdout.txt", "output.txt"):
        path = root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        parsed = _final_answer_from_json_text(text)
        if parsed.extracted:
            return FinalAnswer(extracted=True, text=parsed.text, source=f"{name}:{parsed.source}")
        if not _looks_like_json(text):
            return FinalAnswer(extracted=True, text=text, source=name)

    return FinalAnswer(extracted=False)


def _read_raw_text(root: Path) -> str:
    parts: list[str] = []
    for name in ("final_message.txt", "nat_agent.log", "nat_agent.stderr", "stdout.txt", "stderr.txt", "output.txt"):
        path = root / name
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def _final_answer_from_json_text(text: str) -> FinalAnswer:
    stripped = text.strip()
    if not stripped:
        return FinalAnswer(extracted=False)
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return _final_answer_from_jsonl(stripped)
    return _final_answer_from_payload(payload, source="json")


def _final_answer_from_jsonl(text: str) -> FinalAnswer:
    final_answer = FinalAnswer(extracted=False)
    saw_json_line = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        saw_json_line = True
        candidate = _final_answer_from_payload(event, source="jsonl")
        if candidate.extracted:
            final_answer = candidate
    if final_answer.extracted or saw_json_line:
        return final_answer
    return FinalAnswer(extracted=False)


def _final_answer_from_payload(payload: Any, *, source: str) -> FinalAnswer:
    if not isinstance(payload, dict):
        return FinalAnswer(extracted=False, source=source)

    for key in ("result", "response", "output", "text"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return FinalAnswer(extracted=True, text=value.strip(), source=f"{source}.{key}")

    content = payload.get("content")
    content_text = _content_to_text(content)
    if content_text:
        return FinalAnswer(extracted=True, text=content_text, source=f"{source}.content")

    message = payload.get("message")
    if isinstance(message, dict):
        content_text = _content_to_text(message.get("content"))
        if content_text:
            return FinalAnswer(extracted=True, text=content_text, source=f"{source}.message.content")

    return FinalAnswer(extracted=False, source=source)


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""
    parts = [part.get("text", "") for part in content if isinstance(part, dict) and isinstance(part.get("text"), str)]
    return "".join(parts).strip()


def _looks_like_json(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("{") or stripped.startswith("[")


def _find_atif_trajectory(root: Path) -> Path | None:
    for relative_path in ("trajectory.json", "atif_trajectory.json", "atif/trajectory.json"):
        path = root / relative_path
        if path.exists() and path.is_file():
            return path
    return None
