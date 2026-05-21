// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { LineChart } from '@mui/x-charts/LineChart';
import type { Entry } from '@nemo/sdk/generated/platform/schema';
import { Stack, Text } from '@nvidia/foundations-react-core';
import {
  countRatingsByDate,
  getUniqueSortedDates,
  mapToLabels,
} from '@studio/components/charts/FeedbackSentimentLineChart/utils';
import { LineChartSkeleton } from '@studio/components/charts/LineChartSkeleton';
import { FC, useMemo } from 'react';

enum GraphAxisId {
  Date = 'date',
  Timestamp = 'timestamp',
  Count = 'count',
}

interface Props {
  entries?: Entry[];
  isPending?: boolean;
  height?: number;
}

export const FeedbackSentimentLineChart: FC<Props> = ({
  entries = [],
  isPending,
  height = 400,
}) => {
  const graphData = useMemo((): Entry[] => {
    return entries.sort((entryA, entryB) => {
      return (
        new Date(entryA.created_at || '').getTime() - new Date(entryB.created_at || '').getTime()
      );
    });
  }, [entries]);

  const xLabels = getUniqueSortedDates(graphData);
  const positiveData = countRatingsByDate(graphData, true);
  const negativeData = countRatingsByDate(graphData, false);

  if (isPending) {
    return <LineChartSkeleton />;
  }

  return (
    <>
      <Stack gap="density-sm">
        <Text kind="title/sm">Feedback</Text>
        <div>
          <Text className="text-lg">{entries?.length} </Text>
          <Text>Feedback Entries</Text>
        </div>
      </Stack>
      <LineChart
        grid={{ horizontal: true }}
        height={height}
        xAxis={[
          {
            id: GraphAxisId.Date,
            label: 'Date',
            data: xLabels,
            scaleType: 'point',
          },
        ]}
        yAxis={[
          {
            id: GraphAxisId.Count,
            label: 'Count',
          },
        ]}
        series={[
          {
            label: 'Positive',
            data: mapToLabels(positiveData, xLabels),
            color: 'var(--text-color-brand)',
            xAxisId: GraphAxisId.Date,
            showMark: mapToLabels(positiveData, xLabels).length <= 1,
          },
          {
            label: 'Negative',
            data: mapToLabels(negativeData, xLabels),
            color: 'var(--text-color-accent-red)',
            xAxisId: GraphAxisId.Date,
            showMark: mapToLabels(negativeData, xLabels).length <= 1,
          },
        ]}
        slotProps={{
          legend: {
            direction: 'row',
            position: { vertical: 'top', horizontal: 'right' },
            itemMarkWidth: 12,
            itemMarkHeight: 12,
            labelStyle: {
              fontSize: 12,
              lineHeight: '12px',
              fill: 'var(--text-color-base)',
            },
          },
        }}
      />
    </>
  );
};
