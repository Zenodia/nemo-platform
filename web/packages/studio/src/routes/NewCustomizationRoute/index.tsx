// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { AccessibleTitle } from '@studio/components/AccessibleTitle';
import { NewCustomizationForm } from '@studio/components/NewCustomizationForm';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { useBreadcrumbs } from '@studio/providers/breadcrumbs/useBreadcrumbs';
import { getCustomizationJobListRoute } from '@studio/routes/utils';
import { FC } from 'react';

export const NewCustomizationRoute: FC = () => {
  const workspace = useWorkspaceFromPath();

  useBreadcrumbs({
    items: [
      {
        href: getCustomizationJobListRoute(workspace),
        slotLabel: 'Custom Models',
      },
      {
        slotLabel: 'New Fine-Tuned Model',
      },
    ],
  });
  return (
    <AccessibleTitle title={`New fine-tuned model for ${workspace}`}>
      <NewCustomizationForm />
    </AccessibleTitle>
  );
};
