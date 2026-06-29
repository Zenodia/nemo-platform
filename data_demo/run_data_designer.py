"""04-Data toy example — synthetic dataset generator.

Demonstrates the NeMo Platform Data Designer capability:
generate diverse, structured synthetic QA pairs from a seed document
ready to feed into an evaluation pipeline (e.g. 02-Evaluate / run_eval.py).

The generation strategy mirrors what NeMo Data Designer does internally:
  - Multiple *personas* produce different question styles and difficulty levels.
  - Multiple *rounds* over the same document surface different aspects.
  - An *adversarial* persona generates edge-case / tricky questions.
  - Output is JSONL with the same schema as qa_eval.jsonl, so the eval
    pipeline can consume it directly without further conversion.

In production, NeMo Data Designer adds:
  - Managed pipelines for generation at scale via the Jobs service
  - Deduplication, quality filtering, and diversity scoring
  - Direct output to the NeMo Files service for downstream jobs

No GPU required — uses the inference API only.

Prereqs:
  INFERENCE_API_KEY  set in the environment

Run:
  python data_demo/run_data_designer.py
  python data_demo/run_data_designer.py --rounds 3 --output my_dataset.jsonl
  python data_demo/run_data_designer.py --seed-file path/to/doc.txt
"""

from __future__ import annotations

import argparse
import json
import os
import textwrap
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

INFERENCE_BASE_URL = "https://inference-api.nvidia.com"
MODEL = "aws/anthropic/bedrock-claude-sonnet-4-6"
DEFAULT_OUTPUT = Path(__file__).parent / "synthetic_dataset.jsonl"

# ---------------------------------------------------------------------------
# Default seed document (swap via --seed-file for your own domain)
# ---------------------------------------------------------------------------

DEFAULT_SEED_DOCUMENT = textwrap.dedent("""\
    NeMo Platform is NVIDIA's production toolkit for making AI agents safer,
    more accurate, and cheaper to run.

    NeMo Guardrails protects agents at the Inference Gateway layer using
    content-safety rails that block jailbreaks, harmful content, and PII
    leakage. Rails come in two modes: self-check (the main LLM judges its
    own output) and content-safety (a dedicated NemoGuard classifier model).

    The NeMo Evaluator runs systematic benchmarks using deterministic metrics
    such as BLEU and ROUGE, as well as LLM-as-judge metrics that score
    semantic correctness. Evaluation jobs can run locally via the SDK or
    remotely as managed platform jobs.

    The NeMo skill optimizer searches over prompt strategies and
    hyperparameters to find the configuration that maximises evaluation score.
    It integrates with Switchyard to route queries dynamically to the
    best-fitting model based on query complexity or domain.

    NeMo Data Designer generates synthetic training and evaluation datasets
    from seed documents. It supports persona-based generation, adversarial
    question creation, and topic-diversity controls. Output goes to the NeMo
    Files service for use by downstream evaluation or fine-tuning jobs.

    The NeMo Agent Toolkit (NAT) enables building LangGraph-based agents that
    can be deployed, evaluated, and optimised within the platform lifecycle.
""")

# ---------------------------------------------------------------------------
# Personas — each produces a different question style
# ---------------------------------------------------------------------------

@dataclass
class Persona:
    name: str
    instruction: str

PERSONAS: list[Persona] = [
    Persona(
        "curious student",
        "Ask a simple, clear factual question a student new to this topic would ask.",
    ),
    Persona(
        "technical practitioner",
        "Ask a precise how-to or architectural question a developer or ML engineer needs answered.",
    ),
    Persona(
        "product evaluator",
        "Ask a comparative question that distinguishes between two features or approaches in the document.",
    ),
    Persona(
        "adversarial tester",
        (
            "Ask a tricky question that probes the limits of the document's content — "
            "for example a question where the answer is subtle, counter-intuitive, or "
            "requires combining two distinct facts from the document."
        ),
    ),
]

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

GENERATOR_SYSTEM = """\
You are a synthetic QA dataset generator.
Given a seed document and a persona, produce ONE question-answer pair.

Rules:
  - The question must be fully answerable from the document alone.
  - The answer must be grounded in the document; do not add outside knowledge.
  - Keep the answer concise but complete (1-3 sentences).
  - Vary your question from any you have generated before.

Return ONLY valid JSON with these exact keys:
  "user_input":         the question string
  "retrieved_contexts": a JSON array containing the single most relevant
                        sentence or passage from the document (as a string)
  "reference":          the gold answer string
  "persona":            the persona name string
"""

DEDUP_SYSTEM = """\
You are a quality-control filter.
Given a list of questions that have already been generated, decide whether a
new candidate question is sufficiently different from all of them.

Return ONLY valid JSON: {"accept": true | false, "reason": "<one sentence>"}
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _chat(client: OpenAI, system: str, user: str, temperature: float = 0.7) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=512,
    )
    return resp.choices[0].message.content or ""


def _parse_json(raw: str) -> dict | None:
    text = raw.strip()
    if "```" in text:
        parts = text.split("```")
        text = parts[1].lstrip("json").strip() if len(parts) > 1 else text
    try:
        return json.loads(text)
    except Exception:
        return None


def _generate_pair(client: OpenAI, document: str, persona: Persona) -> dict | None:
    prompt = (
        f"Persona: {persona.name}\n"
        f"Persona instruction: {persona.instruction}\n\n"
        f"Seed document:\n{document.strip()}"
    )
    raw = _chat(client, GENERATOR_SYSTEM, prompt, temperature=0.8)
    data = _parse_json(raw)
    if data is None:
        return None
    # Normalise: ensure retrieved_contexts is a list
    ctx = data.get("retrieved_contexts", [])
    if isinstance(ctx, str):
        data["retrieved_contexts"] = [ctx]
    data.setdefault("persona", persona.name)
    return data


def _is_duplicate(client: OpenAI, existing_questions: list[str], candidate: str) -> bool:
    if not existing_questions:
        return False
    prompt = (
        f"Existing questions:\n"
        + "\n".join(f"  - {q}" for q in existing_questions[-10:])  # last 10 is enough
        + f"\n\nCandidate: {candidate}"
    )
    raw = _chat(client, DEDUP_SYSTEM, prompt, temperature=0.0)
    data = _parse_json(raw)
    if data is None:
        return False  # conservative: accept on parse failure
    return not bool(data.get("accept", True))

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--rounds", type=int, default=2,
                        help="Generation rounds per persona (default: 2). "
                             "Total target = rounds × personas.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Output JSONL path (default: data_demo/synthetic_dataset.jsonl)")
    parser.add_argument("--seed-file", type=Path, default=None,
                        help="Path to a plain-text seed document. "
                             "Defaults to the built-in NeMo Platform description.")
    parser.add_argument("--no-dedup", action="store_true",
                        help="Skip the deduplication LLM check (faster, more duplicates).")
    args = parser.parse_args()

    api_key = os.environ.get("INFERENCE_API_KEY")
    if not api_key:
        raise SystemExit("Set INFERENCE_API_KEY in the environment before running.")

    document = DEFAULT_SEED_DOCUMENT
    if args.seed_file:
        document = args.seed_file.read_text(encoding="utf-8")
        print(f"  Seed document: {args.seed_file}  ({len(document)} chars)")

    client = OpenAI(api_key=api_key, base_url=INFERENCE_BASE_URL)

    target = args.rounds * len(PERSONAS)
    print(f"\n{'='*64}")
    print("NeMo Platform — 04-Data: Synthetic Dataset Generator")
    print(f"Model    : {MODEL}")
    print(f"Personas : {len(PERSONAS)}  |  Rounds: {args.rounds}  |  Target: {target} records")
    print(f"Output   : {args.output}")
    print(f"{'='*64}\n")

    records: list[dict] = []
    existing_questions: list[str] = []
    skipped = 0

    for round_num in range(1, args.rounds + 1):
        print(f"  Round {round_num}/{args.rounds}")
        for persona in PERSONAS:
            print(f"    [{persona.name}] generating ...", end=" ", flush=True)
            record = _generate_pair(client, document, persona)

            if record is None:
                print("parse error — skipped")
                skipped += 1
                continue

            question = record.get("user_input", "")

            # Deduplication check
            if not args.no_dedup and _is_duplicate(client, existing_questions, question):
                print(f"duplicate — skipped  ({question[:50]}...)")
                skipped += 1
                continue

            existing_questions.append(question)
            records.append(record)
            print(f"OK  Q: {question[:60]}{'...' if len(question) > 60 else ''}")

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as fh:
        for rec in records:
            # Write only the fields the eval pipeline expects; keep persona as metadata
            fh.write(json.dumps(rec) + "\n")

    print(f"\n{'='*64}")
    print(f"Generated {len(records)} records  (skipped {skipped})")
    print(f"Output  → {args.output}")
    print(f"{'='*64}\n")

    print("Sample records:\n")
    for rec in records[:3]:
        print(f"  [{rec.get('persona', '?')}]")
        print(f"  Q : {rec.get('user_input', '')}")
        ctx = rec.get('retrieved_contexts', [''])[0]
        print(f"  Ctx: {ctx[:80]}{'...' if len(ctx) > 80 else ''}")
        ans = rec.get('reference', '')
        print(f"  A : {ans[:80]}{'...' if len(ans) > 80 else ''}")
        print()

    print("  Tip: feed this file directly into the 02-Evaluate pipeline:")
    print(f"  python rag_qa_eval/run_eval.py --dataset {args.output}")
    print()


if __name__ == "__main__":
    main()
