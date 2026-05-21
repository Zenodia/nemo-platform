// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useToast } from '@nemo/common/src/providers/toast/useToast';
import type { MetricEvaluationResponse } from '@nemo/sdk/generated/platform/schema';
import { Badge, CodeSnippet, Flex, Stack, Text } from '@nvidia/foundations-react-core';
import type { FC } from 'react';

function formatScoreValue(value: number): string {
  return String(value);
}

function buildRowResultLines(
  rowScores: MetricEvaluationResponse['row_scores'],
  scoreOrder: string[]
): string[] {
  const lines: string[] = [];
  const sorted = [...rowScores].sort((a, b) => a.index - b.index);

  for (const row of sorted) {
    if (row.scores) {
      const seen = new Set<string>();
      for (const name of scoreOrder) {
        if (name in row.scores) {
          seen.add(name);
          lines.push(`Row ${row.index}: ${name} = ${formatScoreValue(row.scores[name])}`);
        }
      }
      for (const [name, value] of Object.entries(row.scores)) {
        if (seen.has(name)) continue;
        lines.push(`Row ${row.index}: ${name} = ${formatScoreValue(value)}`);
      }
    } else {
      lines.push(`Row ${row.index}: error = ${row.error ?? 'Unknown error'}`);
    }
  }

  return lines;
}

export const ResultsLog: FC<{ results: MetricEvaluationResponse }> = ({ results }) => {
  const toast = useToast();
  const { aggregate_scores, row_scores } = results;
  const scoreNames = aggregate_scores.map((s) => s.name);
  const resultLines = buildRowResultLines(row_scores, scoreNames);
  const resultText = resultLines.join('\n');

  return (
    <Stack gap="density-lg">
      <Stack gap="density-xs">
        <Text kind="label/bold/sm">Aggregate Scores</Text>
        <Flex gap="density-sm" wrap="wrap">
          {aggregate_scores.map((agg) => (
            <Badge key={agg.name} kind="solid" color="green">
              {agg.name}: mean={'mean' in agg && agg.mean != null ? agg.mean.toFixed(2) : 'N/A'}{' '}
              min={'min' in agg && agg.min != null ? agg.min : 'N/A'} max=
              {'max' in agg && agg.max != null ? agg.max : 'N/A'} (n={agg.count})
            </Badge>
          ))}
        </Flex>
      </Stack>

      <CodeSnippet
        className="w-full min-w-[240px]"
        value={resultText}
        language="shell"
        kind="block"
        collapsible
        rows={20}
        defaultOpen
        slotActions={
          <Text kind="label/bold/md" className="me-auto">
            Results
          </Text>
        }
        onCopySuccess={() => toast.success('Results copied to clipboard')}
        attributes={{
          CodeSnippetCode: { className: 'max-h-[min(40vh,360px)]' },
        }}
      />
    </Stack>
  );
};
