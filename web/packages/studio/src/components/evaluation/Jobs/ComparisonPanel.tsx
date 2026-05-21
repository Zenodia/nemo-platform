// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { TableEmptyState } from '@nemo/common/src/components/TableEmptyState';
import { renderMultipleSelectedValues } from '@nemo/common/src/utils/form';
import {
  Flex,
  Panel,
  Select,
  Spinner,
  Stack,
  StatusMessage,
  Text,
} from '@nvidia/foundations-react-core';
import { useEvaluationJobResultV2 } from '@studio/hooks/evaluation/useEvaluationJobResultV2';
import { useJobsAndResultsV2 } from '@studio/hooks/evaluation/useJobsAndResultsV2';
import { type EvaluationJobV2 } from '@studio/selectors/evaluationJob';
import { prettifyName } from '@studio/util/evaluations';
import { ChartLine, ChartNetwork, TriangleAlert } from 'lucide-react';
import { useState, ReactNode } from 'react';

interface ComparisonPanelV2Props {
  job: EvaluationJobV2;
  workspace: string;
  jobName: string;
}

/**
 * V2 Comparison panel that works with artifact-based results
 */
export const ComparisonPanel = ({ job, workspace, jobName }: ComparisonPanelV2Props) => {
  const [filterMetrics, setFilterMetrics] = useState<string[]>([]);

  const { status } = job ?? {};
  const isPendingStatus = status === 'pending' || status === 'active';

  const { scores, isLoading: isPendingResult } = useEvaluationJobResultV2(workspace, jobName);

  // For now, just show single job - can add comparison features later
  const { rows, allMetrics, activeMetrics } = useJobsAndResultsV2({
    jobs: [job],
    results: [scores],
    filter: { metrics: filterMetrics },
    prettifyName,
  });

  const handleFilterMetrics = (remaining: string[]) => {
    setFilterMetrics(allMetrics.filter((opt) => !remaining.includes(opt)));
  };

  const handleTagClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    if (e.currentTarget.textContent) {
      setFilterMetrics([...filterMetrics, e.currentTarget.textContent]);
    }
  };

  const isLoading = isPendingResult;
  const failedStatus = status === 'error' || status === 'cancelled' || status === 'cancelling';
  const greenStatus = status === 'completed';

  let content: ReactNode;
  if (isPendingStatus) {
    content = (
      <Stack className="max-w-[500px] mx-auto" gap="density-lg">
        <Spinner
          size="large"
          description="Evaluation in progress. Results will be available once complete."
        />
      </Stack>
    );
  } else if (failedStatus) {
    content = (
      <StatusMessage
        className="mx-auto"
        size="medium"
        slotMedia={<TriangleAlert width={65} height={65} />}
        slotHeading="Job Failed"
        slotSubheading="The evaluation job failed. No comparison data available."
      />
    );
  } else if (isLoading) {
    content = <Spinner size="large" description="Loading comparison data..." />;
  } else if (!scores || rows.length === 0) {
    content = (
      <TableEmptyState
        header="No Results"
        emptyMessage="No evaluation results available for comparison"
        icon={<ChartNetwork />}
      />
    );
  } else {
    // Display metrics in a simple table format
    const row = rows[0];
    content = (
      <Stack gap="4" className="w-full">
        <Text kind="title/sm">Metrics Comparison</Text>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-border-default">
                <th className="text-left p-2">
                  <Text kind="label/semibold/sm">Metric</Text>
                </th>
                {Object.keys(row.result?.scores?.[Object.keys(row.result?.scores)[0]] || {}).map(
                  (scoreName) => (
                    <th key={scoreName} className="text-right p-2">
                      <Text kind="label/semibold/sm">{scoreName}</Text>
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {Object.entries(row.result?.scores || {}).map(([metricName, metricScores]) => (
                <tr key={metricName} className="border-b border-border-subtle">
                  <td className="p-2">
                    <Text kind="body/regular/sm">{metricName}</Text>
                  </td>
                  {Object.values(metricScores).map((value, idx) => (
                    <td key={idx} className="text-right p-2">
                      <Text kind="body/semibold/sm">
                        {typeof value === 'number' ? value.toFixed(4) : value}
                      </Text>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Stack>
    );
  }

  return (
    <Panel
      elevation="high"
      slotIcon={<ChartLine />}
      slotHeading={
        <Flex align="center" justify="between" gap="density-lg">
          Detailed Metrics
          {greenStatus && allMetrics.length > 0 && (
            <Select
              id="select-metrics"
              multiple
              placeholder="Select metrics"
              items={allMetrics}
              value={activeMetrics}
              onValueChange={handleFilterMetrics}
              renderValue={(values) =>
                renderMultipleSelectedValues({
                  values,
                  placeholder: 'Select metrics',
                  tagProps: {
                    onClick: handleTagClick,
                  },
                  attributes: {
                    overflowGroup: {
                      kind: 'popover',
                    },
                  },
                })
              }
              attributes={{
                SelectTrigger: {
                  className: 'max-w-[300px] [&_.nv-input-content]:overflow-x-auto',
                },
              }}
            />
          )}
        </Flex>
      }
    >
      {content}
    </Panel>
  );
};
