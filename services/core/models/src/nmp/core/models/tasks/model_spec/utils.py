# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import re
from pathlib import Path
from typing import Any

import yaml

_EMBEDDING_PIPELINE_TAGS = frozenset({"feature-extraction", "sentence-similarity", "text-embeddings-inference"})
_GENERATIVE_PIPELINE_TAGS = frozenset({"text-generation", "text2text-generation", "image-to-text"})
_SUPPORTING_TAGS = frozenset(
    {
        "sentence-transformers",
        "text-embeddings-inference",
        "sentence-similarity",
        "embedding",
        "multimodal",
        "retrieval",
    }
)
_SENTENCE_TRANSFORMER_ARTIFACTS = (
    "modules.json",
    "config_sentence_transformers.json",
    "sentence_bert_config.json",
    "1_Pooling",
)
_FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(.*?)\n---(?:\s*\n|$)", re.DOTALL)


def _load_architectures(config_path: Path) -> list[str]:
    if not config_path.is_file():
        return []

    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []

    architectures = config.get("architectures", [])
    if isinstance(architectures, str):
        return [architectures]
    if isinstance(architectures, list):
        return [str(arch) for arch in architectures]
    return []


def _load_readme_frontmatter(readme_path: Path) -> dict[str, Any]:
    if not readme_path.is_file():
        return {}

    try:
        content = readme_path.read_text(encoding="utf-8")
    except OSError:
        return {}

    match = _FRONTMATTER_PATTERN.search(content)
    if not match:
        return {}

    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}

    if isinstance(parsed, dict):
        return parsed
    return {}


def _normalize_tags(raw_tags: Any) -> set[str]:
    if not isinstance(raw_tags, list):
        return set()
    return {str(tag).strip().lower() for tag in raw_tags if str(tag).strip()}


# TODO: refine this function and replace is_embedding_model with it
# see if we can also use `family` or `tied_embeddings` in the ModelSpec to determine if it's an embedding model.
def is_embedding_model_v2(model_dir: str) -> tuple[bool, str]:
    """
    Analyzes a local Hugging Face model directory to determine if it is an embedding model.

    Args:
        model_dir (str): The path to the downloaded model directory.

    Returns:
        tuple[bool, str]: A boolean indicating if it's an embedding model,
                          and a string explaining the reasoning.
    """

    model_path = Path(model_dir)
    if not model_path.is_dir():
        return False, f"Directory not found: {model_dir}"

    strong_positive_signals: list[str] = []
    strong_negative_signals: list[str] = []
    supporting_signals: list[str] = []

    for artifact in _SENTENCE_TRANSFORMER_ARTIFACTS:
        artifact_path = model_path / artifact
        if artifact == "1_Pooling":
            if artifact_path.is_dir():
                strong_positive_signals.append("artifact:1_Pooling/")
            continue
        if artifact_path.is_file():
            strong_positive_signals.append(f"artifact:{artifact}")

    architectures = _load_architectures(model_path / "config.json")
    generative_architectures = [
        arch for arch in architectures if ("ForCausalLM" in arch or "ForConditionalGeneration" in arch)
    ]
    if generative_architectures:
        strong_negative_signals.append(f"architectures:{'|'.join(generative_architectures)}")

    readme_frontmatter = _load_readme_frontmatter(model_path / "README.md")
    pipeline_tag_raw = readme_frontmatter.get("pipeline_tag")
    pipeline_tag = str(pipeline_tag_raw).strip().lower() if isinstance(pipeline_tag_raw, str) else None
    if pipeline_tag in _EMBEDDING_PIPELINE_TAGS:
        strong_positive_signals.append(f"pipeline_tag:{pipeline_tag}")
    if pipeline_tag in _GENERATIVE_PIPELINE_TAGS:
        strong_negative_signals.append(f"pipeline_tag:{pipeline_tag}")

    tags = _normalize_tags(readme_frontmatter.get("tags"))
    supporting_tags = sorted(tags.intersection(_SUPPORTING_TAGS))
    if supporting_tags:
        supporting_signals.append(f"tags:{'|'.join(supporting_tags)}")

    if (model_path / "generation_config.json").is_file():
        strong_negative_signals.append("file:generation_config.json")

    if strong_positive_signals:
        details = ",".join(strong_positive_signals)
        if supporting_signals:
            details = f"{details};supporting={','.join(supporting_signals)}"
        return True, f"strong_positive:{details}"

    if strong_negative_signals:
        details = ",".join(strong_negative_signals)
        if supporting_signals:
            details = f"{details};supporting={','.join(supporting_signals)}"
        return False, f"strong_negative:{details}"

    if supporting_signals:
        return False, f"inconclusive:supporting={','.join(supporting_signals)}"
    return False, "inconclusive:no_strong_embedding_signals"
