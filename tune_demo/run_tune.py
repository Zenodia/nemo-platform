"""03-Tune toy example — prompt strategy optimizer.

Demonstrates the NeMo Platform skill-optimization loop:
  1. Define candidate prompt strategies (system prompt + temperature).
  2. Run each strategy against a fixed evaluation dataset.
  3. Score every response with an LLM judge (same model, self-check pattern).
  4. Rank strategies and report the winner.

In production the NeMo skill optimizer wraps this same loop with:
  - Systematic hyperparameter search over a larger strategy space
  - Distributed evaluation across bigger datasets via the Evaluator service
  - Automatic promotion of the winning config to the deployed agent

No GPU required — uses the inference API only.

Prereqs:
  INFERENCE_API_KEY  set in the environment

Run:
  python tune_demo/run_tune.py
  python tune_demo/run_tune.py --verbose    # show each Q/A/score
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field

from openai import OpenAI

INFERENCE_BASE_URL = "https://inference-api.nvidia.com"
MODEL = "aws/anthropic/bedrock-claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# Candidate strategies — each is a (system_prompt, temperature) pair.
# This mirrors what the NeMo skill optimizer searches over.
# ---------------------------------------------------------------------------

@dataclass
class Strategy:
    name: str
    system: str
    temperature: float

STRATEGIES: list[Strategy] = [
    Strategy(
        name="Terse",
        system="Answer in one sentence only. No preamble.",
        temperature=0.0,
    ),
    Strategy(
        name="Explanatory",
        system=(
            "You are a knowledgeable assistant. "
            "Provide accurate, well-explained answers with concrete examples where helpful."
        ),
        temperature=0.3,
    ),
    Strategy(
        name="Structured",
        system=(
            "Always answer in this exact format:\n"
            "Answer: <direct one-line answer>\n"
            "Why: <one-sentence explanation>"
        ),
        temperature=0.0,
    ),
    Strategy(
        name="Chain-of-thought",
        system=(
            "Think through the question step by step before giving your final answer. "
            "End with 'Final answer: <answer>'."
        ),
        temperature=0.2,
    ),
]

# ---------------------------------------------------------------------------
# Fixed evaluation dataset
# ---------------------------------------------------------------------------

@dataclass
class EvalRow:
    question: str
    reference: str  # gold answer used by the judge

EVAL_DATASET: list[EvalRow] = [
    EvalRow(
        "What is photosynthesis?",
        "The process by which plants use sunlight, water, and CO2 to produce glucose and oxygen.",
    ),
    EvalRow(
        "What does RAM stand for and what is its purpose?",
        "Random Access Memory; temporary fast-access storage for data the CPU is actively using.",
    ),
    EvalRow(
        "What is the key difference between TCP and UDP?",
        "TCP guarantees ordered, reliable delivery via handshake; UDP is connectionless and faster but lossy.",
    ),
    EvalRow(
        "What is gradient descent?",
        "An iterative optimisation algorithm that adjusts model weights in the direction that minimises loss.",
    ),
    EvalRow(
        "What does a transformer's attention mechanism do?",
        "It computes weighted relationships between all tokens in a sequence so each token attends to relevant context.",
    ),
]

# ---------------------------------------------------------------------------
# Judge prompt — mirrors NeMo's LLM-as-judge scoring
# ---------------------------------------------------------------------------

JUDGE_SYSTEM = """\
You are an answer-quality evaluator.
Compare the AI answer to the reference answer for the same question and score 0–4:
  4 = fully correct, clear, and complete
  3 = mostly correct with minor gaps
  2 = partially correct
  1 = mostly incorrect
  0 = wrong or absent

Return ONLY valid JSON with exactly two keys:
  "score": integer 0–4
  "reason": one-sentence justification
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _chat(client: OpenAI, system: str, user: str, temperature: float = 0.0) -> str:
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


def _judge(client: OpenAI, row: EvalRow, answer: str) -> tuple[int, str]:
    payload = (
        f"Question:  {row.question}\n"
        f"Reference: {row.reference}\n"
        f"AI answer: {answer}"
    )
    raw = _chat(client, JUDGE_SYSTEM, payload, temperature=0.0)
    try:
        text = raw.strip()
        if "```" in text:
            text = text.split("```")[1].lstrip("json").strip()
        data = json.loads(text)
        return int(data.get("score", 0)), str(data.get("reason", ""))
    except Exception:
        return 0, f"parse error: {raw[:80]}"


@dataclass
class StrategyResult:
    strategy: Strategy
    scores: list[int] = field(default_factory=list)

    @property
    def avg(self) -> float:
        return sum(self.scores) / len(self.scores) if self.scores else 0.0

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print each question, answer, and judge score.")
    args = parser.parse_args()

    api_key = os.environ.get("INFERENCE_API_KEY")
    if not api_key:
        raise SystemExit("Set INFERENCE_API_KEY in the environment before running.")

    client = OpenAI(api_key=api_key, base_url=INFERENCE_BASE_URL)

    print(f"\n{'='*64}")
    print("NeMo Platform — 03-Tune: Prompt Strategy Optimizer")
    print(f"Model      : {MODEL}")
    print(f"Strategies : {len(STRATEGIES)}  |  Eval dataset: {len(EVAL_DATASET)} rows")
    print(f"{'='*64}\n")

    results: list[StrategyResult] = []

    for strategy in STRATEGIES:
        print(f"  Evaluating [{strategy.name}]")
        if args.verbose:
            print(f"    system   : {strategy.system[:80]!r}")
            print(f"    temp     : {strategy.temperature}")

        result = StrategyResult(strategy=strategy)
        for row in EVAL_DATASET:
            answer = _chat(client, strategy.system, row.question, temperature=strategy.temperature)
            score, reason = _judge(client, row, answer)
            result.scores.append(score)
            if args.verbose:
                print(f"    Q: {row.question}")
                print(f"    A: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                print(f"    → score={score}/4  {reason}")
                print()

        print(f"    avg score : {result.avg:.2f} / 4.0   per-row: {result.scores}")
        print()
        results.append(result)

    # Rank and report
    ranked = sorted(results, key=lambda r: r.avg, reverse=True)
    winner = ranked[0]

    print(f"{'='*64}")
    print("Rankings")
    print(f"{'='*64}")
    for i, r in enumerate(ranked, 1):
        crown = " ← WINNER" if i == 1 else ""
        print(f"  {i}. {r.strategy.name:20s}  avg={r.avg:.2f}/4.0{crown}")

    print()
    print(f"  Best strategy : [{winner.strategy.name}]")
    print(f"  System prompt : {winner.strategy.system!r}")
    print(f"  Temperature   : {winner.strategy.temperature}")
    print()
    print("  Next step in NeMo Platform: promote this config to the deployed")
    print("  agent via 'nemo agents optimize-skills' or update the agent YAML.")
    print()


if __name__ == "__main__":
    main()
