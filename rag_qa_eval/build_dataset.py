"""Convert qa_toy_example.csv into a NeMo Evaluator dataset (JSONL).

The CSV columns are: <index>, Context, Answer, Question.

We emit one JSON object per row using the field names RAGAS metrics expect:

    user_input          -> the Question
    retrieved_contexts  -> [Context]   (RAGAS requires a list of strings)
    reference           -> the Answer  (ground truth)

This mirrors rag_wJudge.ipynb, where each row already carries its own context
(so no live NeMo Retriever call is needed) and we score the generated answer
against the gold Answer plus judge the context relevance to the Question.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = REPO_ROOT / "qa_toy_example.csv"
DEFAULT_OUT = Path(__file__).resolve().parent / "qa_eval.jsonl"


def build(csv_path: Path, out_path: Path, limit: int | None) -> int:
    df = pd.read_csv(csv_path)
    # First unnamed column is just the row index; ignore it.
    required = {"Context", "Answer", "Question"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{csv_path} is missing columns: {sorted(missing)}")

    if limit is not None:
        df = df.head(limit)

    rows_written = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for _, row in df.iterrows():
            question = str(row["Question"]).strip()
            context = str(row["Context"]).strip()
            answer = str(row["Answer"]).strip()
            if not question or not context:
                continue
            record = {
                "user_input": question,
                "retrieved_contexts": [context],
                "reference": answer,
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            rows_written += 1
    return rows_written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Source CSV path.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output JSONL path.")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only convert the first N rows (handy for a smoke test).",
    )
    args = parser.parse_args()

    count = build(args.csv, args.out, args.limit)
    print(f"Wrote {count} rows to {args.out}")


if __name__ == "__main__":
    main()
