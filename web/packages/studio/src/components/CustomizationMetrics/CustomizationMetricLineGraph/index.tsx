// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { LineChart } from '@mui/x-charts';
import { prefixDummyPoint } from '@studio/components/charts/utils';
import type { CustomizationMetricValue } from '@studio/types/customization';
import { FC, useMemo } from 'react';

enum GraphAxisId {
  Step = 'step',
  DataLoss = 'dataLoss',
}

interface Props {
  dataLoss: CustomizationMetricValue[];
  height: number;
}

export const CustomizationMetricLineGraph: FC<Props> = ({ dataLoss, height }) => {
  const graphData = useMemo((): CustomizationMetricValue[] => {
    return prefixDummyPoint({ list: dataLoss, defaultValues: { step: 0, value: 0 } }).sort(
      (a, b) => {
        if (!a?.step || !b?.step) {
          return 0;
        }
        if (a.step < b.step) {
          return -1;
        } else if (a.step > b.step) {
          return 1;
        }
        return 0;
      }
    );
  }, [dataLoss]);

  return (
    <LineChart
      height={height}
      xAxis={[
        {
          id: GraphAxisId.Step,
          label: 'Steps',
          data: graphData.map((stepData) => stepData?.step ?? null),
          valueFormatter: (stepNumber: number, { location }) =>
            location === 'tooltip' ? `Step ${stepNumber}` : `${stepNumber}`,
        },
      ]}
      yAxis={[
        {
          id: GraphAxisId.DataLoss,
          label: 'Data Loss',
        },
      ]}
      series={[
        {
          data: graphData.map((stepData) => stepData?.value ?? null),
          xAxisKey: GraphAxisId.Step,
          color: 'var(--color-green-700)',
          showMark: false,
        },
      ]}
      bottomAxis={GraphAxisId.Step}
    />
  );
};
