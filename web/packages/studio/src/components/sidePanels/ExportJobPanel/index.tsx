// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { KVPair } from '@nemo/common/src/components/KVPair';
import { StatusBadge } from '@nemo/common/src/components/StatusBadge';
import { IJobTerminalStatuses } from '@nemo/common/src/constants/query';
import { useLiveSeconds } from '@nemo/common/src/hooks/useLiveSeconds';
import {
  formatTimeInSeconds,
  getDifferenceInMilliseconds,
  utcToLocalDate,
} from '@nemo/common/src/utils/date';
import { unknownToString } from '@nemo/common/src/utils/formatters';
import { getJobRefetchInterval } from '@nemo/common/src/utils/query';
import { useGetExportJobStatus } from '@nemo/sdk/generated/platform/api';
import { Divider, Flex, SidePanel, Stack, Text } from '@nvidia/foundations-react-core';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { ComponentProps } from 'react';

type Props = {
  exportJobId: string;
  attributes?: {
    SidePanel?: ComponentProps<typeof SidePanel>;
  };
};
export const ExportJobPanel = ({ exportJobId, attributes = {} }: Props) => {
  const workspace = useWorkspaceFromPath();
  const { data: job } = useGetExportJobStatus(workspace, exportJobId, {
    query: {
      refetchInterval: (query) => getJobRefetchInterval(query.state.data?.status),
    },
  });
  const isTerminalStatus = job?.status && IJobTerminalStatuses.includes(job.status);
  const liveSeconds = useLiveSeconds({
    startDate: job?.created_at ? utcToLocalDate(job.created_at) : undefined,
    enabled: !isTerminalStatus,
  });
  const differenceInMilliseconds = getDifferenceInMilliseconds(job?.created_at, job?.updated_at);
  const elapsedSeconds = differenceInMilliseconds
    ? Math.floor(differenceInMilliseconds / 1000)
    : undefined;

  const duration = isTerminalStatus ? formatTimeInSeconds(elapsedSeconds) : liveSeconds;
  const hasFilters = job?.config.filters && Object.keys(job.config.filters).length > 0;
  return (
    <SidePanel
      slotHeading="Export Job Details"
      modal
      className="w-[440px]"
      bordered
      {...attributes.SidePanel}
    >
      <Stack gap="4">
        <KVPair
          label="Status"
          value={
            <Flex gap="1">
              <StatusBadge status={job?.status} /> {duration ? duration : ''}
            </Flex>
          }
        />
        <KVPair label="Job ID" value={job?.id} />
        <KVPair label="Destination" value={job?.output_file_url} />
        {hasFilters && (
          <>
            <Divider />
            <Text kind="label/semibold/lg">Filters</Text>
            {Object.entries(job?.config.filters ?? {}).map(([key, value]) => (
              <KVPair key={key} label={key} value={unknownToString(value)} />
            ))}
          </>
        )}
      </Stack>
    </SidePanel>
  );
};
