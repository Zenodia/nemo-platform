// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Breadcrumbs as KuiBreadcrumbs } from '@nvidia/foundations-react-core';
import { WORKSPACE_BREADCRUMB_ITEM } from '@studio/components/Breadcrumbs/constants';
import { useBreadcrumbs } from '@studio/providers/breadcrumbs/useBreadcrumbs';
import { FC, useMemo } from 'react';
import { Link, useParams } from 'react-router-dom';

export const Breadcrumbs: FC = () => {
  const { breadcrumbs } = useBreadcrumbs();
  const { workspace } = useParams();

  const items = useMemo(() => {
    const allItems = [];
    if (workspace) {
      allItems.push(WORKSPACE_BREADCRUMB_ITEM);
    }
    return allItems.concat(
      breadcrumbs.map(({ href = '#', slotLabel }) => ({
        children: <Link to={href}>{slotLabel}</Link>,
      }))
    );
  }, [breadcrumbs, workspace]);

  return <KuiBreadcrumbs items={items} />;
};
