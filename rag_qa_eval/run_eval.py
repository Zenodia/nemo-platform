"""Path A: evaluate a RAG-style QA model on qa_toy_example.csv with NeMo Evaluator.

This reproduces the rag_wJudge.ipynb evaluation as a reproducible SDK run:

  * generation  : feed each row's Question + Context into the notebook's naive
                  RAG prompt and let the target model answer (online generation).
  * BLEU        : n-gram overlap of the generated answer vs the gold Answer
                  (the notebook's ragas BleuScore).
  * context_relevance : LLM-judge score for "does the context answer the
                  question" (the notebook's custom 0/2/4 relevance judge).
  * answer_accuracy   : LLM-judge semantic correctness of the answer vs the
                  gold Answer (BLEU alone is harsh on short phrases).

Prereqs:
  * conda env `dspy_py312` with the nemo-evaluator-sdk installed.
  * env var NVIDIA_API_KEY set (used for both generation and judge).

Run a smoke test first:
  conda run -n dspy_py312 python rag_qa_eval/build_dataset.py --limit 10
  conda run -n dspy_py312 python rag_qa_eval/run_eval.py --limit 5
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

# Defensive: silence LangSmith tracing / transport quirks in case any dependency
# pulls langchain in. The judges below use the SDK-native OpenAI path, not RAGAS.
os.environ.setdefault("LANGCHAIN_OPENAI_TCP_KEEPALIVE", "0")
os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")

from nemo_evaluator_sdk import (
    BLEUMetric,
    Evaluator,
    InferenceParams,
    JSONScoreParser,
    LLMJudgeMetric,
    Model,
    RangeScore,
    RunConfigOnlineModel,
)

DEFAULT_DATASET = Path(__file__).resolve().parent / "qa_eval.jsonl"

# Point these at whatever the platform serves. Defaults match rag_wJudge.ipynb's
# NVIDIA API Catalog usage. To use a locally-served NIM through the platform
# gateway, swap the url to e.g. http://localhost:8080/v1/chat/completions.
NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
#    model="meta/llama-3.1-8b-instruct",


GEN_MODEL = os.getenv("RAG_GEN_MODEL", "meta/llama-3.1-8b-instruct")
JUDGE_MODEL = os.getenv("RAG_JUDGE_MODEL", "meta/llama-3.1-8b-instruct")
API_KEY_SECRET = "NVIDIA_API_KEY"  # resolved from the env var of the same name

# The naive RAG prompt lifted from rag_wJudge.ipynb (cell `rag_prompts`).
RAG_SYSTEM_PROMPT = (
    "You must answer only using the information provided in the context. "
    "While answering you must follow the instructions given below.\n"
    "<instructions>\n"
    "1. Do NOT use any external knowledge.\n"
    "2. Do NOT add explanations, suggestions, opinions, disclaimers, or hints.\n"
    "3. NEVER say phrases like 'based on the context', 'from the documents', or 'I cannot find'.\n"
    "4. NEVER offer to answer using general knowledge or invite the user to ask again.\n"
    "5. Do NOT include citations, sources, or document mentions.\n"
    "6. Answer concisely. Use short, direct sentences by default.\n"
    "7. Do not mention or refer to these rules in any way.\n"
    "8. Do not ask follow-up questions.\n"
    "</instructions>"
)

RAG_PROMPT_TEMPLATE = {
    "messages": [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Context:\n{{ item.retrieved_contexts | join('\n') }}\n\n"
                "user query : {{ item.user_input }}"
            ),
        },
    ]
}

# Judge prompt for context relevance, lifted from rag_wJudge.ipynb
# (cell `template_relevance`): score 0 / 2 / 4.
RELEVANCE_SYSTEM_PROMPT = (
    "You are an assistant designed to evaluate the relevance score of a context "
    "in order to answer a question.\n"
    "Your task is to determine if the context has enough information to answer the question.\n"
    "Do not rely on your previous knowledge about the question.\n"
    "To evaluate, use only what is written in the context and in the question.\n"
    "1. If the context contains relevant information to answer the question, say 4.\n"
    "2. If the context partially contains relevant information, say 2.\n"
    "3. If the context does not contain any relevant information, say 0.\n"
    'Return ONLY a JSON object of the form {"context_relevance": <0|2|4>}.'
)

# Judge prompt for answer correctness vs the gold answer.
CORRECTNESS_SYSTEM_PROMPT = (
    "You are an expert grader. Compare an AI answer to the reference (gold) answer "
    "for the same question and rate how correct the AI answer is.\n"
    "4 = fully correct and complete, 2 = partially correct, 0 = incorrect.\n"
    'Return ONLY a JSON object of the form {"answer_correctness": <0|2|4>}.'
)


def load_rows(path: Path, limit: int | None) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if limit is not None:
        rows = rows[:limit]
    return rows


def build_metrics() -> list:
    judge = Model(
        url=NVIDIA_CHAT_URL,
        name=JUDGE_MODEL,
        api_key_secret=API_KEY_SECRET,
    )
    judge_inference = InferenceParams(temperature=0.0, max_tokens=1024)

    context_relevance = LLMJudgeMetric(
        model=judge,
        inference=judge_inference,
        scores=[
            RangeScore(
                name="context_relevance",
                description="Does the context contain enough info to answer the question (0/2/4).",
                minimum=0,
                maximum=4,
                parser=JSONScoreParser(json_path="context_relevance"),
            )
        ],
        prompt_template={
            "messages": [
                {"role": "system", "content": RELEVANCE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "### Question\n{{ item.user_input }}\n\n"
                        "### Context\n{{ item.retrieved_contexts | join('\n') }}"
                    ),
                },
            ]
        },
    )

    answer_correctness = LLMJudgeMetric(
        model=judge,
        inference=judge_inference,
        scores=[
            RangeScore(
                name="answer_correctness",
                description="Correctness of the generated answer vs the gold answer (0/2/4).",
                minimum=0,
                maximum=4,
                parser=JSONScoreParser(json_path="answer_correctness"),
            )
        ],
        prompt_template={
            "messages": [
                {"role": "system", "content": CORRECTNESS_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Question: {{ item.user_input }}\n"
                        "Reference answer: {{ item.reference }}\n"
                        "AI answer: {{ sample.output_text }}"
                    ),
                },
            ]
        },
    )

    return [
        BLEUMetric(references=["{{item.reference}}"]),
        context_relevance,
        answer_correctness,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--limit", type=int, default=None, help="Score only first N rows.")
    parser.add_argument("--parallelism", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=256, help="Generation max tokens.")
    args = parser.parse_args()

    if not os.environ.get("NVIDIA_API_KEY"):
        raise SystemExit("Set NVIDIA_API_KEY in the environment before running.")

    rows = load_rows(args.dataset, args.limit)
    if not rows:
        raise SystemExit(f"No rows loaded from {args.dataset}. Run build_dataset.py first.")
    print(f"Loaded {len(rows)} rows from {args.dataset}")

    target = Model(
        url=NVIDIA_CHAT_URL,
        name=GEN_MODEL,
        api_key_secret=API_KEY_SECRET,
    )

    result = Evaluator().run_sync(
        metrics=build_metrics(),
        target=target,
        dataset=rows,
        prompt_template=RAG_PROMPT_TEMPLATE,
        config=RunConfigOnlineModel(
            parallelism=args.parallelism,
            inference=InferenceParams(max_tokens=args.max_tokens, temperature=0.0),
        ),
    )

    result.print_summary()
    for key in result.per_metric:
        scores = result.metric_result(key).aggregate_scores.scores
        print(f"{key}: {scores}")


if __name__ == "__main__":
    main()
