// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Badge, Block, Card, Flex, Panel, Stack, Text } from '@nvidia/foundations-react-core';
import type { EvaluatorOutput } from '@studio/routes/agents/AgentEvaluationsRoute/api';
import { EvaluatorReasoning } from '@studio/routes/agents/AgentEvaluationsRoute/components/EvaluatorReasoning';
import { formatScore, scoreColor } from '@studio/routes/agents/AgentEvaluationsRoute/evalScores';
import { FlaskConical } from 'lucide-react';
import type { FC } from 'react';

interface EvaluatorOutputPanelProps {
  output: EvaluatorOutput;
}

export const EvaluatorOutputPanel: FC<EvaluatorOutputPanelProps> = ({ output }) => {
  return (
    <Panel
      slotHeading={
        <>
          <span className="capitalize">{output.evaluator}</span> ({output.items.length} item
          {output.items.length === 1 ? '' : 's'})
        </>
      }
      slotIcon={<FlaskConical />}
      elevation="high"
      density="compact"
    >
      <Stack gap="density-2xl">
        <Flex gap="density-md" align="center">
          <Text kind="body/bold/md">Average score</Text>
          <Badge kind="solid" color={scoreColor(output.averageScore)}>
            {formatScore(output.averageScore)}
          </Badge>
        </Flex>
        {output.items.length === 0 ? (
          <Block className="text-subtle">No per-item results recorded.</Block>
        ) : (
          // One card per item — the tunable_rag_evaluator's reasoning has
          // 4–5 substructures (question / expected / generated / breakdown /
          // judge), which crammed into a table cell becomes unreadable.
          <Stack gap="density-lg">
            {output.items.map((item, idx) => (
              <Card key={`${item.id}-${idx}`} className="relative">
                {/* Pin the score chip to the card's top-right corner so it
                    reads as a status indicator and doesn't push the
                    reasoning content down. ``pr-density-3xl`` on the
                    content stack reserves room so long Question/Expected
                    text doesn't run under the badge. */}
                <div className="absolute top-density-md right-density-md">
                  <Badge kind="outline" color={scoreColor(item.score)}>
                    {formatScore(item.score)}
                  </Badge>
                </div>
                <Stack gap="density-lg" className="pr-density-3xl">
                  {item.error ? (
                    <Text kind="body/regular/sm" color="danger">
                      {item.error}
                    </Text>
                  ) : (
                    <EvaluatorReasoning reasoning={item.reasoning} />
                  )}
                </Stack>
              </Card>
            ))}
          </Stack>
        )}
      </Stack>
    </Panel>
  );
};
