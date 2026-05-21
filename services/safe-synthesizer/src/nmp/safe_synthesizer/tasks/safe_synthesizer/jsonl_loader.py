# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""JSONL file loading utilities with unicode and escaping support.

This module provides functions to load JSONL files that may have:
1. Unicode escape sequences (like \\u2019) that PyArrow's JSON parser struggles with
2. Improperly escaped curly/smart quotes from data conversion
"""

import json
import logging
import re

import pandas as pd

logger = logging.getLogger("safe_synthesizer")


def try_repair_json_line(line: str) -> str:
    """Attempt to repair common JSON escaping issues in JSONL files.

    Some JSONL files have curly/smart quotes improperly converted to escaped quotes
    at the end of JSON string values (e.g., text\\"} instead of text"}).
    This function attempts to fix such issues.

    Args:
        line: A single line from a JSONL file.

    Returns:
        The repaired line (or original if no repair was needed).
    """
    # Pattern: \" immediately before }, ], or , (end of JSON value)
    # This fixes cases where curly quotes were improperly escaped
    return re.sub(r'\\"(\s*[},\]])', r'"\1', line)


def load_jsonl_file(filepath: str, strict: bool = False) -> pd.DataFrame:
    """Load a JSONL file using Python's json module with repair logic.

    This function handles JSONL files that may have:
    1. Unicode escape sequences (like \\u2019) that PyArrow's JSON parser struggles with
    2. Improperly escaped curly/smart quotes

    Args:
        filepath: Path to the JSONL file.
        strict: If True, raise an error if any lines cannot be parsed.
                If False (default), skip malformed lines with a warning.

    Returns:
        A pandas DataFrame containing the parsed records.

    Raises:
        ValueError: If strict=True and the file contains malformed JSON that cannot be repaired,
                    or if the file contains no valid records.
    """
    records = []
    errors = []
    repaired_count = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            # First, try to parse as-is
            try:
                records.append(json.loads(line))
                continue
            except json.JSONDecodeError:
                pass

            # Try to repair common escaping issues
            repaired_line = try_repair_json_line(line)
            try:
                records.append(json.loads(repaired_line))
                repaired_count += 1
                logger.debug("Repaired JSON escaping issue on line %d", line_num)
                continue
            except json.JSONDecodeError as e:
                errors.append((line_num, str(e)))

    if repaired_count > 0:
        logger.info("Repaired %d lines with JSON escaping issues", repaired_count)

    if errors:
        error_summary = "; ".join(f"line {ln}: {err[:50]}" for ln, err in errors[:5])
        if len(errors) > 5:
            error_summary += f"; ... and {len(errors) - 5} more errors"

        if strict:
            raise ValueError(
                f"JSONL file contains {len(errors)} malformed JSON lines that could not be repaired. "
                f"First errors: {error_summary}"
            )
        else:
            logger.warning(
                "Skipped %d malformed JSON lines that could not be repaired. First errors: %s",
                len(errors),
                error_summary,
            )

    if not records:
        raise ValueError("JSONL file contains no valid records")

    return pd.DataFrame(records)
