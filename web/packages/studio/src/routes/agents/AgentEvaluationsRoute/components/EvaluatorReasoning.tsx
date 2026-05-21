// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Badge, Flex, Stack, Text } from '@nvidia/foundations-react-core';
import type {
  EvalScoreBreakdown,
  EvaluatorOutputItem,
} from '@studio/routes/agents/AgentEvaluationsRoute/api';
import { LabeledSection } from '@studio/routes/agents/AgentEvaluationsRoute/components/LabeledSection';
import { formatScore, scoreColor } from '@studio/routes/agents/AgentEvaluationsRoute/evalScores';
import type { FC } from 'react';

interface EvaluatorReasoningProps {
  reasoning: EvaluatorOutputItem['reasoning'];
}

/** Renders the per-item ``reasoning`` payload from a nat-eval evaluator
 *  output. The ``tunable_rag_evaluator`` writes a structured object with
 *  question / expected / generated / per-component score breakdown / judge
 *  reasoning; other evaluators may write a plain string — fall through to a
 *  single ``Text`` render in that case. */
export const EvaluatorReasoning: FC<EvaluatorReasoningProps> = ({ reasoning }) => {
  if (typeof reasoning === 'string') {
    return (
      <Text kind="body/regular/sm" color="secondary">
        {reasoning}
      </Text>
    );
  }

  const breakdown = reasoning.score_breakdown;
  return (
    <Stack gap="density-xl">
      {reasoning.question && (
        <LabeledSection label="Question">
          <Text kind="body/regular/sm">{reasoning.question}</Text>
        </LabeledSection>
      )}
      {reasoning.answer_description && (
        <LabeledSection label="Expected">
          <Text kind="body/regular/sm">{reasoning.answer_description}</Text>
        </LabeledSection>
      )}
      {reasoning.generated_answer !== undefined && (
        <LabeledSection label="Generated">
          <Text kind="body/regular/sm">{reasoning.generated_answer || '(empty)'}</Text>
        </LabeledSection>
      )}
      {breakdown && Object.keys(breakdown).length > 0 && (
        <LabeledSection label="Score breakdown">
          <Flex gap="density-md" wrap="wrap">
            {Object.entries(breakdown as EvalScoreBreakdown).map(([k, v]) => (
              <Badge key={k} kind="outline" color={scoreColor(v)}>
                {k.replace(/_score$/, '').replace(/_/g, ' ')}: {formatScore(v)}
              </Badge>
            ))}
          </Flex>
        </LabeledSection>
      )}
      {reasoning.reasoning && (
        <LabeledSection label="Judge reasoning">
          <Text kind="body/regular/sm">{reasoning.reasoning}</Text>
        </LabeledSection>
      )}
    </Stack>
  );
};
