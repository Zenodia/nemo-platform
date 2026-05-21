// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PieChart, PieItemIdentifier } from '@mui/x-charts';
import { ThumbDirection } from '@nemo/sdk/generated/platform/schema';
import { Text } from '@nvidia/foundations-react-core';
import {
  THUMBS_UP_LABEL,
  THUMBS_DOWN_LABEL,
} from '@studio/components/charts/FeedbackRatingPieChart/constants';
import { PieCenterLabels } from '@studio/components/charts/PieCenterLabels';
import { PieChartSkeleton } from '@studio/components/charts/PieChartSkeleton';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { getIntakeEntriesRoute } from '@studio/routes/utils';
import React from 'react';
import { useNavigate } from 'react-router';

interface ThumbsPieChartProps {
  height?: number;
  isPending?: boolean;
  thumbsUp?: {
    raw: number;
    percentage: number;
  };
  thumbsDown?: {
    raw: number;
    percentage: number;
  };
}

export function FeedbackRatingPieChart({
  height = 400,
  isPending,
  thumbsUp,
  thumbsDown,
}: ThumbsPieChartProps) {
  const workspace = useWorkspaceFromPath();
  const navigate = useNavigate();

  if (isPending || !thumbsUp || !thumbsDown) {
    return <PieChartSkeleton height={height} />;
  }

  const totalThumbs = thumbsUp.raw + thumbsDown.raw;
  const data = [
    { value: thumbsUp.raw, label: THUMBS_UP_LABEL, color: 'var(--color-green-700)' },
    { value: thumbsDown.raw, label: THUMBS_DOWN_LABEL, color: 'var(--color-red-700)' },
  ].sort((a, b) => {
    return a.value - b.value;
  });

  const handleItemClick = (
    _: React.MouseEvent<SVGPathElement, MouseEvent>,
    params: PieItemIdentifier
  ) => {
    const rating =
      data[params.dataIndex].label === THUMBS_UP_LABEL ? ThumbDirection.up : ThumbDirection.down;
    navigate(getIntakeEntriesRoute(workspace, { filter: { user_rating: { thumb: rating } } }));
  };

  return (
    <>
      <Text kind="title/sm">Feedback Ratings</Text>
      <PieChart
        series={[
          {
            data: totalThumbs ? data : [],
            innerRadius: '60%',
          },
        ]}
        margin={{ left: 1, right: 1, top: 1, bottom: 1 }}
        onItemClick={handleItemClick}
        height={height}
        slotProps={{
          legend: {
            hidden: true,
          },
        }}
      >
        {totalThumbs && <PieCenterLabels labels={[`${totalThumbs}`, 'Total Ratings']} />}
      </PieChart>
    </>
  );
}
