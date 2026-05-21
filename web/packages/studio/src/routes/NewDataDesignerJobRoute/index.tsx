// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PageHeader, Stack } from '@nvidia/foundations-react-core';
import { AccessibleTitle } from '@studio/components/AccessibleTitle';
import { NewDataDesignerJobForm } from '@studio/components/NewDataDesignerJobForm';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { useBreadcrumbs } from '@studio/providers/breadcrumbs/useBreadcrumbs';
import { getDataDesignerJobListRoute } from '@studio/routes/utils';
import type { FC } from 'react';

export const NewDataDesignerJobRoute: FC = () => {
  const workspace = useWorkspaceFromPath();

  useBreadcrumbs({
    items: [
      { href: getDataDesignerJobListRoute(workspace), slotLabel: 'Data Designer' },
      { slotLabel: 'New Job' },
    ],
  });

  return (
    <AccessibleTitle title="New Data Designer Job">
      <Stack className="h-full overflow-auto" gap="density-2xl" padding="density-2xl">
        <PageHeader
          slotHeading="New Data Designer Job"
          slotDescription="Describe what type of content you want to generate. A model will create the job specification for you."
        />
        <NewDataDesignerJobForm />
      </Stack>
    </AccessibleTitle>
  );
};
