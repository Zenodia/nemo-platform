// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { KVPair } from '@nemo/common/src/components/KVPair';
import { formatAbsoluteTimestamp } from '@nemo/common/src/components/RelativeTime/util';
import { useGetApp, useGetEntry, useGetTask } from '@nemo/sdk/generated/platform/api';
import type { Entry } from '@nemo/sdk/generated/platform/schema';
import { Anchor, Panel, Stack } from '@nvidia/foundations-react-core';
import { IntakeThreadPanel } from '@studio/components/IntakeThreadPanel';
import { Loading } from '@studio/components/Layouts/Loading';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { parseAppRef } from '@studio/util/entries';
import { formatKeyLabel } from '@studio/util/strings';
import { Sliders } from 'lucide-react';
import { FC, useState, type ReactNode } from 'react';
import { useParams } from 'react-router-dom';

/** API may return fields not yet reflected on the generated Entry schema. */
type EntryDetail = Entry & {
  description?: string;
  ownership?: {
    created_by?: string;
    updated_by?: string;
    access_policies?: unknown;
  };
  custom_fields?: Record<string, unknown>;
};

/**
 * Route component for the intake entry Metadata tab.
 * Displays comprehensive metadata for the entry organized into groups:
 * - Entry group (ID, external ID, description, thread ID, model, user ID, created, updated)
 * - App group (ID, name, description)
 * - Task group (ID, name, description)
 * - Tracing group (trace ID, session ID)
 * - Request Metadata group (conditional - all request properties except messages/model)
 * - Response Metadata group (conditional - all response properties except choices)
 * - Ownership group (conditional - created by, updated by, access policies)
 * - Custom Fields group (conditional - dynamic key-value pairs)
 *
 * Used as a child of IntakeEntryLayout which provides the header and navigation.
 */
export const IntakeEntryMetadataRoute: FC = () => {
  const { [ROUTE_PARAMS.entryId]: entryId } = useParams() as { [ROUTE_PARAMS.entryId]: string };
  const workspace = useWorkspaceFromPath();
  const { data: entry, isLoading: isLoadingEntry } = useGetEntry(workspace, entryId);

  // Parse app reference to get namespace and app name
  const appParts = parseAppRef(entry?.context?.app);

  // Fetch App entity if context.app is present
  const { data: app, isLoading: isLoadingApp } = useGetApp(workspace, appParts?.appName ?? '', {
    query: { enabled: !!appParts },
  });

  // Fetch Task entity if context.task is present
  const { data: task, isLoading: isLoadingTask } = useGetTask(
    workspace,
    appParts?.appName ?? '',
    entry?.context?.task ?? '',
    { query: { enabled: !!appParts && !!entry?.context?.task } }
  );

  // Thread panel state
  const [threadPanelOpen, setThreadPanelOpen] = useState(false);
  const threadId = entry?.context?.thread_id;

  // Show loading state
  if (isLoadingEntry || isLoadingApp || isLoadingTask) {
    return <Loading description="Loading metadata..." />;
  }

  if (!entry) {
    return null;
  }

  const detail = entry as EntryDetail;

  // Get request properties excluding 'messages' and 'model' (model is shown in Entry group)
  const requestProps = entry.data?.request
    ? Object.entries(entry.data.request).filter(([key]) => key !== 'messages' && key !== 'model')
    : [];

  // Get response properties excluding 'choices' for dynamic rendering
  const responseProps = entry.data?.response
    ? Object.entries(entry.data.response).filter(([key]) => key !== 'choices')
    : [];

  // Check if we have ownership info to display (`access_policies` is unknown — wrap in Boolean so JSX `{hasOwnership && ...}` is not typed as unknown)
  const hasOwnership = Boolean(
    detail.ownership &&
    (detail.ownership.created_by || detail.ownership.updated_by || detail.ownership.access_policies)
  );

  // Check if we have custom fields to display
  const hasCustomFields = Boolean(
    detail.custom_fields && Object.keys(detail.custom_fields).length > 0
  );

  // Helper to format values, showing "—" for missing/null values
  const formatValue = (value: unknown): string => {
    if (value === null || value === undefined || value === '') return '—';
    if (typeof value === 'string') return value;
    if (typeof value === 'number') return value.toLocaleString();
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    return String(value);
  };

  // Helper to render complex values (objects/arrays) as formatted JSON
  const renderComplexValue = (value: unknown): ReactNode => {
    if (value === null || value === undefined) return '—';
    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
      return formatValue(value);
    }
    // For objects/arrays, display as formatted JSON
    return (
      <pre className="text-xs font-mono whitespace-pre-wrap break-words max-w-full">
        {JSON.stringify(value, null, 2)}
      </pre>
    );
  };

  return (
    <Panel elevation="high" slotIcon={<Sliders />} slotHeading="Metadata">
      <Stack gap="density-2xl">
        {/* Entry Group */}
        <Stack gap="density-md">
          <KVPair label="Entry ID" value={formatValue(entry.id)} />
          <KVPair label="External ID" value={formatValue(entry.external_id)} />
          <KVPair label="Description" value={formatValue(detail.description)} />
          <KVPair
            label="Thread ID"
            value={
              threadId ? (
                <Anchor asChild>
                  <button onClick={() => setThreadPanelOpen(true)} className="cursor-pointer">
                    {threadId}
                  </button>
                </Anchor>
              ) : (
                '—'
              )
            }
          />
          <KVPair label="Model" value={formatValue(entry.data?.request?.model)} />
          <KVPair label="User ID" value={formatValue(entry.context?.user_id)} />
          <KVPair
            label="Created"
            value={entry.created_at ? formatAbsoluteTimestamp(entry.created_at) : '—'}
          />
          <KVPair
            label="Updated"
            value={entry.updated_at ? formatAbsoluteTimestamp(entry.updated_at) : '—'}
          />
        </Stack>

        {/* App Group */}
        <Stack gap="density-md">
          <KVPair label="App ID" value={formatValue(entry.context?.app)} />
          <KVPair label="App Name" value={formatValue(app?.name)} />
          <KVPair label="App Description" value={formatValue(app?.description)} />
        </Stack>

        {/* Task Group */}
        <Stack gap="density-md">
          <KVPair label="Task ID" value={formatValue(entry.context?.task)} />
          <KVPair label="Task Name" value={formatValue(task?.name)} />
          <KVPair label="Task Description" value={formatValue(task?.description)} />
        </Stack>

        <Stack gap="density-md">
          <KVPair label="Trace ID" value={formatValue(entry.context?.trace_id)} />
          <KVPair label="Session ID" value={formatValue(entry.context?.session_id)} />
        </Stack>

        {/* Request Metadata Group (conditional) */}
        {requestProps.length > 0 && (
          <Stack gap="density-md">
            {requestProps.map(([key, value]) => (
              <KVPair
                key={key}
                label={formatKeyLabel(key)}
                value={renderComplexValue(value) as ReactNode}
              />
            ))}
          </Stack>
        )}

        {/* Response Metadata Group (conditional) */}
        {responseProps.length > 0 && (
          <Stack gap="density-md">
            {responseProps.map(([key, value]) => (
              <KVPair
                key={key}
                label={formatKeyLabel(key)}
                value={renderComplexValue(value) as ReactNode}
              />
            ))}
          </Stack>
        )}

        {/* Ownership Group (conditional) */}
        {hasOwnership && (
          <Stack gap="density-md">
            <KVPair label="Created By" value={formatValue(detail.ownership?.created_by)} />
            <KVPair label="Updated By" value={formatValue(detail.ownership?.updated_by)} />
            <KVPair
              label="Access Policies"
              value={renderComplexValue(detail.ownership?.access_policies) as ReactNode}
            />
          </Stack>
        )}

        {/* Custom Fields Group (conditional) */}
        {hasCustomFields && (
          <Stack gap="density-md">
            {Object.entries(detail.custom_fields!).map(([key, value]) => (
              <KVPair
                key={key}
                label={formatKeyLabel(key)}
                value={renderComplexValue(value) as ReactNode}
              />
            ))}
          </Stack>
        )}
      </Stack>
      {threadId && (
        <IntakeThreadPanel
          threadId={threadId}
          open={threadPanelOpen}
          onOpenChange={setThreadPanelOpen}
        />
      )}
    </Panel>
  );
};
