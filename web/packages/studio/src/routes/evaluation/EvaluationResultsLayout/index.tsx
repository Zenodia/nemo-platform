// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Button, PageHeader, Stack } from '@nvidia/foundations-react-core';
import { AccessibleTitle } from '@studio/components/AccessibleTitle';
import { Loading } from '@studio/components/Layouts/Loading';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { useBreadcrumbs } from '@studio/providers/breadcrumbs/useBreadcrumbs';
import { getEvaluationMetricsRunRoute } from '@studio/routes/utils';
import { FC, Suspense, useEffect } from 'react';
import { useNavigate, Outlet } from 'react-router-dom';

export const EvaluationResultsLayout: FC = () => {
  const workspace = useWorkspaceFromPath();
  const navigate = useNavigate();

  const { setBreadcrumbs } = useBreadcrumbs();

  useEffect(() => {
    setBreadcrumbs([
      {
        slotLabel: 'Evaluations',
      },
    ]);
  }, [setBreadcrumbs]);

  return (
    <AccessibleTitle title={`Evaluations for ${workspace}`}>
      <Stack className="h-full overflow-auto" gap="density-2xl" padding="density-2xl">
        <PageHeader
          className="p-0"
          slotHeading="Evaluations"
          slotActions={
            <Stack className="grow" align="end">
              <Button
                color="brand"
                onClick={() => navigate(getEvaluationMetricsRunRoute(workspace))}
              >
                Evaluate Model
              </Button>
            </Stack>
          }
        />
        <Suspense fallback={<Loading description="Loading..." />}>
          <Outlet />
        </Suspense>
      </Stack>
    </AccessibleTitle>
  );
};
