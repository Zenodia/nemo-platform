// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export interface NodeRange {
  start: number;
  end: number;
}

/**
 * Finds the ranges of JSON objects in a string.
 *
 * This function parses a string containing JSON objects and identifies the start and end positions
 * of each complete JSON object. It's particularly useful for JSONL files where each line is a
 * separate JSON object, or for identifying individual objects within a larger JSON structure.
 *
 * The function works by tracking opening and closing braces to identify complete JSON objects.
 * It maintains a bracket count to handle nested objects correctly.
 *
 * @param doc - The string containing JSON objects to parse
 * @returns An array of NodeRange objects, each containing the start and end positions of a JSON object
 */
export function findNodeRanges(doc: string): NodeRange[] {
  const ranges: NodeRange[] = [];
  let bracketCount = 0; // Tracks the nesting level of braces
  let nodeStartPos = -1; // Position where the current object starts

  for (let pos = 0; pos < doc.length; pos++) {
    const char = doc[pos];

    // When we find an opening brace, increment the bracket count
    if (char === '{') {
      bracketCount++;
      // If this is the first opening brace (not nested), mark it as the start of a new object
      if (bracketCount === 1) {
        nodeStartPos = pos;
      }
    }
    // When we find a closing brace, decrement the bracket count
    else if (char === '}') {
      bracketCount--;
      // If we've closed all open braces and we have a valid start position,
      // we've found a complete JSON object
      if (bracketCount === 0 && nodeStartPos !== -1) {
        ranges.push({ start: nodeStartPos, end: pos + 1 });
        nodeStartPos = -1; // Reset for the next object
      }
    }
  }

  return ranges;
}
