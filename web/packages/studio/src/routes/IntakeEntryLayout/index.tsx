// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useGetEntry } from '@nemo/sdk/generated/platform/api';
import { Button, PageHeader, Stack, StatusMessage, Tabs } from '@nvidia/foundations-react-core';
import { AccessibleTitle } from '@studio/components/AccessibleTitle';
import { IntakeThreadPanel } from '@studio/components/IntakeThreadPanel';
import { Loading } from '@studio/components/Layouts/Loading';
import { NotFound } from '@studio/components/Layouts/NotFound';
import { ROUTE_PARAMS, ROUTES } from '@studio/constants/routes';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { useBreadcrumbs } from '@studio/providers/breadcrumbs/useBreadcrumbs';
import {
  getIntakeEntryMessagesRoute,
  getIntakeEntryEventsRoute,
  getIntakeEntryMetadataRoute,
  getIntakeRoute,
} from '@studio/routes/utils';
import { CircleAlert as ErrorIcon } from 'lucide-react';
import { FC, Suspense, useState } from 'react';
import { Link, Outlet, matchPath, useLocation, useParams } from 'react-router-dom';

/**
 * Layout component for the Intake Entry detail section.
 * Provides shared header and tab navigation for Messages, Events, and Metadata sub-routes.
 * Child routes are rendered via <Outlet />.
 */
export const IntakeEntryLayout: FC = () => {
  const workspace = useWorkspaceFromPath();
  const { [ROUTE_PARAMS.entryId]: entryId } = useParams() as { [ROUTE_PARAMS.entryId]: string };

  const { data: entry, error, isLoading } = useGetEntry(workspace, entryId);
  const eventsCount = entry?.events?.length ?? 0;
  const threadId = entry?.context?.thread_id;

  // Thread panel state
  const [threadPanelOpen, setThreadPanelOpen] = useState(false);

  const location = useLocation();
  const match = matchPath(
    { path: `${ROUTES.workspace.intakeEntry}/:selectedTab`, end: false },
    location.pathname
  );
  const {
    params: { selectedTab },
  } = match ?? { params: { selectedTab: 'messages' } };

  const messagesRoute = getIntakeEntryMessagesRoute(workspace, entryId);
  const eventsRoute = getIntakeEntryEventsRoute(workspace, entryId);
  const metadataRoute = getIntakeEntryMetadataRoute(workspace, entryId);

  useBreadcrumbs({
    items: [
      {
        slotLabel: 'Intake',
        href: getIntakeRoute(workspace),
      },
      {
        slotLabel: 'Entry',
      },
    ],
  });

  // Show NotFound for 404 errors
  if (error?.status === 404) {
    return (
      <NotFound
        subheader="Entry Not Found"
        message="The entry you're looking for doesn't exist or you don't have permission to view it."
      />
    );
  }

  // Show loading state
  if (isLoading) {
    return <Loading description="Loading entry..." />;
  }

  // Show generic error for other errors
  if (error) {
    return (
      <StatusMessage
        className="mx-auto mt-density-2xl"
        size="medium"
        slotMedia={<ErrorIcon width={65} height={65} />}
        slotHeading="Error loading entry"
        slotSubheading={error.message}
      />
    );
  }

  return (
    <AccessibleTitle title={`Entry ${entryId}`}>
      <Stack gap="density-2xl" padding="density-2xl" className="h-full overflow-auto">
        <PageHeader
          className="p-0"
          slotHeading={`Entry ${entryId}`}
          slotActions={
            threadId && (
              <Button kind="secondary" onClick={() => setThreadPanelOpen(true)}>
                View Thread
              </Button>
            )
          }
        />
        <Tabs
          // Override KUI's default overflow:hidden since we're using Tabs purely for
          // navigation (with renderLink), not for containing tab panel content.
          className="overflow-visible"
          value={selectedTab}
          items={[
            { value: 'messages', children: 'Input/Output', href: messagesRoute },
            {
              value: 'events',
              children: `Events & Annotations (${eventsCount})`,
              href: eventsRoute,
            },
            { value: 'metadata', children: 'Metadata', href: metadataRoute },
          ]}
          renderLink={(item) => <Link to={item.href!}>{item.children}</Link>}
        />
        <Suspense fallback={<Loading description="Loading..." />}>
          <Outlet />
        </Suspense>
      </Stack>
      {threadId && (
        <IntakeThreadPanel
          threadId={threadId}
          open={threadPanelOpen}
          onOpenChange={setThreadPanelOpen}
        />
      )}
    </AccessibleTitle>
  );
};
