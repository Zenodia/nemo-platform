// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { badgeStatus, type BadgeStatus } from '@nemo/common/src/components/StatusBadge/badgeStatus';
import { Badge } from '@nvidia/foundations-react-core';

export type { BadgeStatus };

interface StatusBadgeProps<T = string> {
  status: BadgeStatus<T> | undefined;
}

export const StatusBadge = <T extends string = string>({ status }: StatusBadgeProps<T>) => {
  const getBadge = (status: BadgeStatus<T> | undefined) => {
    if (!status) return badgeStatus.default;

    // Normalize for APIs that use SCREAMING_SNAKE (e.g. ModelProviderStatus) vs lowercase job statuses
    const statusKey = String(status).toLowerCase();
    if (statusKey in badgeStatus) {
      return badgeStatus[statusKey as keyof typeof badgeStatus];
    }

    return badgeStatus.default;
  };

  const badge = getBadge(status);

  return (
    <Badge color={badge.color} kind="solid">
      {badge.icon ? <badge.icon width="12px" height="12px" role="img" /> : null}
      {badge.label}
    </Badge>
  );
};
