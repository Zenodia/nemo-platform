// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Badge, Block, Flex, Panel, Stack, Text } from '@nvidia/foundations-react-core';
import type {
  EvaluatorOutput,
  WorkflowOutputItem,
} from '@studio/routes/agents/AgentEvaluationsRoute/api';
import { formatScore, scoreColor } from '@studio/routes/agents/AgentEvaluationsRoute/evalScores';
import { MessagesSquare } from 'lucide-react';
import { useMemo, type FC } from 'react';

interface WorkflowOutputPanelProps {
  items: WorkflowOutputItem[];
  evaluatorOutputs?: EvaluatorOutput[];
}

interface ScoreLookup {
  /** Per-evaluator score for one workflow item, looked up by ``id``. */
  byEvaluator: Map<string, number | null>;
}

const buildScoreLookups = (evaluatorOutputs: EvaluatorOutput[]): Map<string, ScoreLookup> => {
  // Outer key is the workflow item's ``id`` stringified — nat-eval ids can be
  // numeric or string, and JSON serialises them differently across files.
  const out = new Map<string, ScoreLookup>();
  for (const evalOut of evaluatorOutputs) {
    for (const item of evalOut.items) {
      const key = String(item.id);
      let entry = out.get(key);
      if (!entry) {
        entry = { byEvaluator: new Map() };
        out.set(key, entry);
      }
      entry.byEvaluator.set(evalOut.evaluator, item.score);
    }
  }
  return out;
};

export const WorkflowOutputPanel: FC<WorkflowOutputPanelProps> = ({
  items,
  evaluatorOutputs = [],
}) => {
  const scoreLookups = useMemo(() => buildScoreLookups(evaluatorOutputs), [evaluatorOutputs]);
  const evaluatorNames = useMemo(
    () => evaluatorOutputs.map((e) => e.evaluator),
    [evaluatorOutputs]
  );
  const showScores = evaluatorNames.length > 0;

  return (
    <Panel
      slotHeading={`Agent responses (${items.length} item${items.length === 1 ? '' : 's'})`}
      slotIcon={<MessagesSquare />}
      elevation="high"
      density="compact"
    >
      <Stack gap="density-md">
        {items.length === 0 ? (
          <Block className="text-subtle">No workflow output recorded.</Block>
        ) : (
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="border-b border-base">
                <th className="py-density-sm pr-density-md w-12 align-top">
                  <Text kind="label/bold/sm">ID</Text>
                </th>
                <th className="py-density-sm pr-density-md align-top">
                  <Text kind="label/bold/sm">Question</Text>
                </th>
                <th className="py-density-sm pr-density-md align-top">
                  <Text kind="label/bold/sm">Expected</Text>
                </th>
                <th className="py-density-sm pr-density-md align-top">
                  <Text kind="label/bold/sm">Generated</Text>
                </th>
                {showScores && (
                  <th className="py-density-sm align-top w-48">
                    <Text kind="label/bold/sm">Scores</Text>
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {items.map((item, idx) => {
                const lookup = scoreLookups.get(String(item.id));
                return (
                  <tr
                    key={`${item.id}-${idx}`}
                    className="border-b border-base last:border-0 align-top"
                  >
                    <td className="py-density-lg pr-density-lg">
                      <Text kind="body/regular/sm">{String(item.id)}</Text>
                    </td>
                    <td className="py-density-lg pr-density-lg">
                      <Text kind="body/regular/sm">{item.question}</Text>
                    </td>
                    <td className="py-density-lg pr-density-lg">
                      <Text kind="body/regular/sm" color="secondary">
                        {item.answer}
                      </Text>
                    </td>
                    <td className="py-density-lg pr-density-lg">
                      {item.generated_answer ? (
                        <Text kind="body/regular/sm">{item.generated_answer}</Text>
                      ) : (
                        <Text kind="body/regular/sm" color="secondary">
                          (empty)
                        </Text>
                      )}
                    </td>
                    {showScores && (
                      <td className="py-density-lg">
                        <Flex gap="density-xs" wrap="wrap">
                          {evaluatorNames.map((name) => {
                            const score = lookup?.byEvaluator.get(name);
                            return (
                              <Badge key={name} kind="outline" color={scoreColor(score ?? null)}>
                                <span className="capitalize">{name}</span>:{' '}
                                {formatScore(score ?? null)}
                              </Badge>
                            );
                          })}
                        </Flex>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </Stack>
    </Panel>
  );
};
