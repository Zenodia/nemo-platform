# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# Labels for system metrics to use across handlers
LABEL_AGENTIC = "agentic"
LABEL_ADVANCED_REASONING = "advanced_reasoning"
LABEL_QUESTION_ANSWERING = "question_answering"
LABEL_INSTRUCTION_FOLLOWING = "instruction_following"
LABEL_LANGUAGE_UNDERSTANDING = "language_understanding"
LABEL_MATH = "math"
LABEL_CONTENT_SAFETY = "content_safety"
LABEL_CODE = "code"
LABEL_RAG = "rag"
LABEL_RETRIEVAL = "retrieval"


def new_labels(harness: str, category: str) -> dict:
    return {"eval_harness": harness, "eval_category": category}
