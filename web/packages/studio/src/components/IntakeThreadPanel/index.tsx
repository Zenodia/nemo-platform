// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useSetTimeout } from '@nemo/common/src/hooks/useSetTimeout';
import { useListEntries } from '@nemo/sdk/generated/platform/api';
import type { EntrySortField } from '@nemo/sdk/generated/platform/schema';
import { SidePanel } from '@nvidia/foundations-react-core';
import { ThreadConversation } from '@studio/components/IntakeThreadPanel/components/ThreadConversation';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { getIntakeEntryRoute } from '@studio/routes/utils';
import { FC, useCallback } from 'react';
import { useNavigate } from 'react-router';

interface IntakeThreadPanelProps {
  threadId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const IntakeThreadPanel: FC<IntakeThreadPanelProps> = ({ threadId, open, onOpenChange }) => {
  const navigate = useNavigate();
  const workspace = useWorkspaceFromPath();

  const { data, isLoading, error } = useListEntries(workspace, {
    filter: { context: { thread_id: threadId } },
    sort: 'created_at' as EntrySortField, // Oldest to newest (chronological)
  });

  // Animation delay matches SidePanel exit animation duration (see useDeferredUnmount)
  const PANEL_EXIT_ANIMATION_MS = 300;
  const [setAnimationTimeout] = useSetTimeout();

  const handleViewEntry = useCallback(
    (entryId: string) => {
      // Close the panel first to trigger exit animation
      onOpenChange(false);

      // Wait for animation to complete before navigating
      setAnimationTimeout(() => {
        navigate(getIntakeEntryRoute(workspace, entryId));
      }, PANEL_EXIT_ANIMATION_MS);
    },
    [onOpenChange, navigate, workspace, setAnimationTimeout]
  );

  const entries = data?.data ?? [];

  return (
    <SidePanel
      open={open}
      onOpenChange={onOpenChange}
      slotHeading={`Thread: ${threadId}`}
      bordered
      modal
      className="w-[600px]"
    >
      {isLoading && <div>Loading...</div>}
      {error && <div>Error: {error.message}</div>}
      {entries.length === 0 && !isLoading && <div>No entries found in this thread.</div>}
      {entries.length > 0 && <ThreadConversation entries={entries} onViewEntry={handleViewEntry} />}
    </SidePanel>
  );
};
