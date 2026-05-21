// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PageHeader, Stack, Tabs } from '@nvidia/foundations-react-core';
import { AccessibleTitle } from '@studio/components/AccessibleTitle';
import { ExportEntriesButton } from '@studio/components/buttons/ExportEntriesButton';
import { FeatureFlagBadge } from '@studio/components/FeatureFlagBadge';
import { Loading } from '@studio/components/Layouts/Loading';
import { ROUTES } from '@studio/constants/routes';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { useBreadcrumbs } from '@studio/providers/breadcrumbs/useBreadcrumbs';
import {
  getIntakeEntriesRoute,
  getIntakeThreadsRoute,
  getIntakeExportJobsRoute,
} from '@studio/routes/utils';
import { FC, Suspense } from 'react';
import { Link, Outlet, matchPath, useLocation } from 'react-router-dom';

/**
 * Layout component for the Intake section.
 * Provides shared header and tab navigation for Entries and Threads sub-routes.
 * Child routes are rendered via <Outlet />.
 */
export const IntakeLayout: FC = () => {
  const workspace = useWorkspaceFromPath();

  const location = useLocation();
  const match = matchPath(
    { path: `${ROUTES.workspace.intake}/:selectedTab`, end: false },
    location.pathname
  );
  const {
    params: { selectedTab },
  } = match ?? { params: { selectedTab: 'entries' } };

  const entriesRoute = getIntakeEntriesRoute(workspace);
  const threadsRoute = getIntakeThreadsRoute(workspace);
  const exportJobsRoute = getIntakeExportJobsRoute(workspace);

  useBreadcrumbs({
    items: [
      {
        slotLabel: 'Intake',
      },
    ],
  });

  return (
    <AccessibleTitle title="Intake">
      <Stack gap="density-2xl" padding="density-2xl" className="h-full">
        <PageHeader
          className="p-0"
          slotHeading={
            <>
              Intake
              <FeatureFlagBadge flag="intakeEnabled" />
            </>
          }
          slotActions={<ExportEntriesButton />}
        />
        <Tabs
          // Override KUI's default overflow:hidden since we're using Tabs purely for
          // navigation (with renderLink), not for containing tab panel content.
          className="overflow-visible"
          value={selectedTab}
          items={[
            { value: 'entries', children: 'Entries', href: entriesRoute },
            { value: 'threads', children: 'Threads', href: threadsRoute },
            { value: 'export-jobs', children: 'Export Jobs', href: exportJobsRoute },
          ]}
          renderLink={(item) => <Link to={item.href!}>{item.children}</Link>}
        />
        <Suspense fallback={<Loading description="Loading..." />}>
          <Outlet />
        </Suspense>
      </Stack>
    </AccessibleTitle>
  );
};
