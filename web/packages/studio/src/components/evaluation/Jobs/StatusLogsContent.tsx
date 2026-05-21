// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { LogViewer } from '@nemo/common/src/components/LogViewer';
import { useJobLogs } from '@nemo/common/src/hooks/useJobLogs';
import { FC } from 'react';

interface StatusLogsContentProps {
  workspace: string;
  jobName: string;
}

export const StatusLogsContent: FC<StatusLogsContentProps> = ({ workspace, jobName }) => {
  const { data: logs, isLoading } = useJobLogs({
    workspace,
    name: jobName,
    enabled: !!jobName,
  });

  return (
    <LogViewer
      logs={logs}
      isLoading={isLoading}
      downloadFilename={`${jobName}-logs.txt`}
      emptyMessage="No status logs available for this job."
    />
  );
};
