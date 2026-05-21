// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ErrorMessage } from '@nemo/common/src/components/ErrorMessage';
import { useEvaluationDownloadMetricJobResultAggregateScores } from '@nemo/sdk/generated/platform/api';
import { Panel, Spinner, Stack, Text, StatusMessage } from '@nvidia/foundations-react-core';
import { prettifyName } from '@studio/util/evaluations';
import { ChartBar, TriangleAlert } from 'lucide-react';
import { type FC } from 'react';

interface ResultsPanelProps {
  workspace: string;
  jobName: string;
  status?: string;
}

const EVALUATIONS_PANEL_HEADING = 'Evaluations';

export const ResultsPanel: FC<ResultsPanelProps> = ({ workspace, jobName, status }) => {
  const isPendingStatus = status === 'pending' || status === 'active';
  const failedStatus = status === 'error' || status === 'cancelled';

  const {
    data: scores,
    isLoading,
    error,
  } = useEvaluationDownloadMetricJobResultAggregateScores(workspace, jobName, {
    query: {
      enabled: !!workspace && !!jobName && !isPendingStatus && !failedStatus,
      retry: 3,
    },
  });

  if (isPendingStatus) {
    return (
      <Panel elevation="high" slotIcon={<ChartBar />} slotHeading={EVALUATIONS_PANEL_HEADING}>
        <Stack className="max-w-[500px] mx-auto" gap="density-lg">
          <Spinner
            size="large"
            description="Evaluation in progress. Results will be available once the job completes."
          />
        </Stack>
      </Panel>
    );
  }

  if (failedStatus) {
    return (
      <Panel elevation="high" slotIcon={<ChartBar />} slotHeading={EVALUATIONS_PANEL_HEADING}>
        <ErrorMessage
          header="Job Failed"
          message="The evaluation job failed. No results available."
        />
      </Panel>
    );
  }

  if (isLoading) {
    return (
      <Panel elevation="high" slotIcon={<ChartBar />} slotHeading={EVALUATIONS_PANEL_HEADING}>
        <Spinner size="large" description="Loading results..." />
      </Panel>
    );
  }

  if (error) {
    return (
      <Panel elevation="high" slotIcon={<ChartBar />} slotHeading={EVALUATIONS_PANEL_HEADING}>
        <StatusMessage
          className="mx-auto"
          size="medium"
          slotMedia={<TriangleAlert width={65} height={65} />}
          slotHeading="Error Loading Results"
          slotSubheading="Failed to load evaluation results. Please try again."
        />
      </Panel>
    );
  }

  if (!scores?.scores?.length) {
    return (
      <Panel elevation="high" slotIcon={<ChartBar />} slotHeading={EVALUATIONS_PANEL_HEADING}>
        <StatusMessage
          className="mx-auto"
          size="medium"
          slotMedia={<TriangleAlert width={65} height={65} />}
          slotHeading="No Results"
          slotSubheading="No evaluation results found for this job."
        />
      </Panel>
    );
  }

  return (
    <Panel elevation="high" slotIcon={<ChartBar />} slotHeading={EVALUATIONS_PANEL_HEADING}>
      <Stack gap="4">
        <Text kind="title/sm">Aggregate Scores</Text>
        <Stack gap="2">
          {scores.scores.map((score) => (
            <div key={score.name}>
              <Text kind="label/semibold/md">{score.name}</Text>
              <Stack gap="1" className="ml-4">
                {Object.entries(score)
                  .filter(
                    ([key, value]) =>
                      key !== 'name' &&
                      key !== 'score_type' &&
                      (typeof value === 'number' || typeof value === 'string')
                  )
                  .map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <Text kind="body/regular/sm">{prettifyName(key)}:</Text>
                      <Text kind="body/semibold/sm">
                        {typeof value === 'number'
                          ? Number.isInteger(value)
                            ? value
                            : value.toFixed(4)
                          : value}
                      </Text>
                    </div>
                  ))}
              </Stack>
            </div>
          ))}
        </Stack>
      </Stack>
    </Panel>
  );
};
