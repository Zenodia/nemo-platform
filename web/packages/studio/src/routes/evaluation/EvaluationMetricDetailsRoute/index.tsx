// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEvaluationGetMetric } from '@nemo/sdk/generated/platform/api';
import type { EvaluatorModel } from '@nemo/sdk/generated/platform/schema/EvaluatorModel';
import type { LLMJudgeMetricResponse } from '@nemo/sdk/generated/platform/schema/LLMJudgeMetricResponse';
import type { RubricScore } from '@nemo/sdk/generated/platform/schema/RubricScore';
import {
  Badge,
  Divider,
  Flex,
  PageHeader,
  Panel,
  Stack,
  Text,
  TextArea,
} from '@nvidia/foundations-react-core';
import { AccessibleTitle } from '@studio/components/AccessibleTitle';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { useBreadcrumbs } from '@studio/providers/breadcrumbs/useBreadcrumbs';
import { getEvaluationMetricsRoute } from '@studio/routes/utils';
import { useRequiredPathParams } from '@studio/util/hooks/useRequiredPathParams';
import type { FC } from 'react';

const getModelName = (model: LLMJudgeMetricResponse['model']): string => {
  if (typeof model === 'string') return model;
  return (model as EvaluatorModel).name;
};

const isLLMJudgeMetricResponse = (data: unknown): data is LLMJudgeMetricResponse => {
  if (typeof data !== 'object' || data === null) return false;
  const obj = data as Record<string, unknown>;
  return obj.type === 'llm-judge' && Array.isArray(obj.scores) && obj.model != null;
};

const isRubricScore = (score: LLMJudgeMetricResponse['scores'][number]): score is RubricScore => {
  return 'rubric' in score;
};

export const EvaluationMetricDetailsRoute: FC = () => {
  const workspace = useWorkspaceFromPath();
  const { id } = useRequiredPathParams([ROUTE_PARAMS.evaluationJobId]);

  const { data } = useEvaluationGetMetric(workspace, id);
  const metric = isLLMJudgeMetricResponse(data) ? data : undefined;

  useBreadcrumbs({
    items: [
      {
        href: getEvaluationMetricsRoute(workspace),
        slotLabel: 'Metrics',
      },
      {
        slotLabel: metric?.name ?? id,
      },
    ],
  });

  if (!metric) return null;

  const promptTemplate =
    typeof metric.prompt_template === 'string' ? metric.prompt_template : undefined;

  return (
    <AccessibleTitle title={`Metric details for ${metric.name ?? id}`}>
      <Stack className="overflow-auto" gap="density-2xl" padding="density-2xl">
        <Flex align="center" justify="center" className="w-full">
          <Stack className="w-full max-w-[1200px]" gap="density-2xl">
            <PageHeader className="p-0" slotHeading={metric.name ?? id} />
            <Panel className="w-full h-full overflow-auto" elevation="high" density="standard">
              <Stack gap="density-2xl">
                {/* Details */}
                <Flex gap="density-2xl" align="start">
                  <Stack className="w-2/5 shrink-0" gap="density-xs">
                    <Text kind="label/bold/lg">Details</Text>
                    <Text kind="body/regular/sm">
                      Basic information about this evaluation metric.
                    </Text>
                  </Stack>
                  <Stack className="flex-1" gap="density-md">
                    <Stack gap="density-xs">
                      <Text kind="label/bold/sm">Name</Text>
                      <Text kind="body/regular/md">{metric.name}</Text>
                    </Stack>
                    {metric.description && (
                      <Stack gap="density-xs">
                        <Text kind="label/bold/sm">Description</Text>
                        <Text kind="body/regular/md">{metric.description}</Text>
                      </Stack>
                    )}
                    <Stack gap="density-xs">
                      <Text kind="label/bold/sm">Type</Text>
                      <Badge kind="solid" color="green">
                        {metric.type ?? 'llm-judge'}
                      </Badge>
                    </Stack>
                  </Stack>
                </Flex>

                <Divider />

                {/* Judge Model */}
                <Flex gap="density-2xl" align="start">
                  <Stack className="w-2/5 shrink-0" gap="density-xs">
                    <Text kind="label/bold/lg">Judge Model</Text>
                    <Text kind="body/regular/sm">
                      The judge is the LLM that will evaluate responses.
                    </Text>
                  </Stack>
                  <Stack className="flex-1" gap="density-xs">
                    <Text kind="label/bold/sm">Model</Text>
                    <Text kind="body/regular/md">{getModelName(metric.model)}</Text>
                  </Stack>
                </Flex>

                <Divider />

                {/* Prompt Template */}
                <Flex gap="density-2xl" align="start">
                  <Stack className="w-2/5 shrink-0" gap="density-xs">
                    <Text kind="label/bold/lg">Prompt Template</Text>
                    <Text kind="body/regular/sm">
                      Instructions for the judge, with variables that get filled from your dataset.
                    </Text>
                  </Stack>
                  <Stack className="flex-1" gap="density-2xl">
                    {metric.system_prompt && (
                      <Stack gap="density-xs">
                        <Text kind="label/bold/sm">System Prompt</Text>
                        <TextArea
                          value={metric.system_prompt}
                          readOnly
                          resizeable="manual"
                          attributes={{
                            TextAreaElement: {
                              className: 'font-mono text-sm',
                              rows: 4,
                            },
                          }}
                        />
                      </Stack>
                    )}
                    {promptTemplate && (
                      <Stack gap="density-xs">
                        <Text kind="label/bold/sm">User Prompt</Text>
                        <TextArea
                          value={promptTemplate}
                          readOnly
                          resizeable="manual"
                          attributes={{
                            TextAreaElement: {
                              className: 'font-mono text-sm',
                              rows: 4,
                            },
                          }}
                        />
                      </Stack>
                    )}
                    {!metric.system_prompt && !promptTemplate && (
                      <Text kind="body/regular/sm" className="text-content-secondary">
                        No prompt template configured.
                      </Text>
                    )}
                  </Stack>
                </Flex>

                <Divider />

                {/* Score Definitions */}
                <Flex gap="density-2xl" align="start">
                  <Stack className="w-2/5 shrink-0" gap="density-xs">
                    <Text kind="label/bold/lg">Score Definitions</Text>
                    <Text kind="body/regular/sm">
                      The scores the judge will produce. Each score can be a numeric range or a
                      rubric with labeled levels.
                    </Text>
                  </Stack>
                  <Stack className="flex-1" gap="density-md">
                    {metric.scores.map((score) => (
                      <Stack
                        key={score.name}
                        gap="density-xs"
                        className="border border-base rounded-lg p-4 bg-surface-raised"
                      >
                        <Flex gap="density-sm" align="center">
                          <Text kind="body/bold/md">{score.name}</Text>
                          {score.description && (
                            <Text kind="body/regular/md">{score.description}</Text>
                          )}
                        </Flex>
                        <Flex gap="density-xs" align="center" wrap="wrap">
                          <Text kind="body/bold/md">
                            {isRubricScore(score) ? 'Rubric' : 'Range'}
                          </Text>
                          {isRubricScore(score) ? (
                            score.rubric.map((item) => (
                              <Badge key={item.label} kind="solid" color="gray">
                                {item.label}: {item.value}
                              </Badge>
                            ))
                          ) : (
                            <Badge kind="solid" color="gray">
                              {score.minimum}&ndash;{score.maximum}
                            </Badge>
                          )}
                        </Flex>
                      </Stack>
                    ))}
                  </Stack>
                </Flex>
              </Stack>
            </Panel>
          </Stack>
        </Flex>
      </Stack>
    </AccessibleTitle>
  );
};
