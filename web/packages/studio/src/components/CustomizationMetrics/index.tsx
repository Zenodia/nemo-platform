// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useCustomizationGetJobStatus } from '@nemo/sdk/vendored/customizer/api';
import { StatusMessage, Flex, Stack, Block } from '@nvidia/foundations-react-core';
import { CustomizationMetricLineGraph } from '@studio/components/CustomizationMetrics/CustomizationMetricLineGraph';
import { ErrorMessageWithRetry } from '@studio/components/ErrorMessageWithRetry';
import { StackedSkeleton } from '@studio/components/StackedSkeleton';
import { hasMetrics } from '@studio/types/customization';
import { FolderOpen } from 'lucide-react';
import { FC } from 'react';

const CUSTOMIZATION_METRIC_GRAPH_HEIGHT_PX = 300;

interface Props {
  customizationJobId: string;
  workspace?: string;
}

export const CustomizationMetrics: FC<Props> = ({ customizationJobId, workspace = '' }) => {
  const { data, isLoading, isError, refetch } = useCustomizationGetJobStatus(
    workspace,
    customizationJobId
  );

  const statusDetails = data?.status_details;
  const trainLoss = hasMetrics(statusDetails) ? statusDetails.metrics?.train_loss : undefined;
  const valLoss = hasMetrics(statusDetails) ? statusDetails.metrics?.val_loss : undefined;

  if (isLoading || data?.status === 'pending') {
    return (
      <Stack gap="density-md">
        <StackedSkeleton count={2} height={CUSTOMIZATION_METRIC_GRAPH_HEIGHT_PX} />
      </Stack>
    );
  }

  if (isError) {
    return (
      <ErrorMessageWithRetry
        message="Failed to fetch customization job metrics"
        onRetry={refetch}
      />
    );
  }

  if (!trainLoss?.length && !valLoss?.length) {
    return (
      <Flex className="h-full" justify="center">
        <StatusMessage
          slotHeading="No activity"
          slotMedia={<FolderOpen className="size-12" />}
          slotSubheading="Train a model and monitor its progress here."
        />
      </Flex>
    );
  }

  return (
    <Stack gap="density-md">
      <Block>
        <h4>Training Loss</h4>
        <CustomizationMetricLineGraph
          dataLoss={trainLoss || []}
          height={CUSTOMIZATION_METRIC_GRAPH_HEIGHT_PX}
        />
      </Block>
      <Block>
        <h4>Validation Loss</h4>
        <CustomizationMetricLineGraph
          dataLoss={valLoss || []}
          height={CUSTOMIZATION_METRIC_GRAPH_HEIGHT_PX}
        />
      </Block>
    </Stack>
  );
};
