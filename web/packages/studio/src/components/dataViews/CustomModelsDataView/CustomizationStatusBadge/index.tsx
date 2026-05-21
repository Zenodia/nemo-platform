// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PlatformJobStatus } from '@nemo/sdk/generated/platform/schema';
import { Badge, BadgeProps } from '@nvidia/foundations-react-core';
import { getFormattedCustomizationStatus } from '@studio/util/customizations';
import { FC } from 'react';

interface Props {
  status: PlatformJobStatus | string;
  progressPercent?: number;
}

// TODO: Rename this to JobStatusBadge
export const CustomizationStatusBadge: FC<Props> = ({ status, progressPercent }) => {
  const getBadgeColor = (): BadgeProps['color'] => {
    switch (status) {
      case 'cancelled':
      case 'failed': {
        return 'red';
      }
      case 'created':
      case 'running': {
        return 'blue';
      }
      case 'pending': {
        return 'yellow';
      }
      case 'completed': {
        return 'green';
      }
      default: {
        return 'gray';
      }
    }
  };

  return (
    <Badge color={getBadgeColor()} kind="solid">
      {getFormattedCustomizationStatus(status, progressPercent)}
    </Badge>
  );
};
