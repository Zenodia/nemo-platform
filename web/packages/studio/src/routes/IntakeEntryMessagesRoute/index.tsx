// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useGetEntry } from '@nemo/sdk/generated/platform/api';
import { Flex, StatusMessage } from '@nvidia/foundations-react-core';
import { IntakeAnnotationPanel } from '@studio/components/IntakeAnnotationPanel';
import { IntakeEntryConversation } from '@studio/components/IntakeEntryConversation';
import { Loading } from '@studio/components/Layouts/Loading';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { CircleAlert as ErrorIcon } from 'lucide-react';
import { FC } from 'react';
import { useParams } from 'react-router-dom';

/**
 * Route component for the intake entry Input/Output tab.
 * Displays the conversation messages from the entry.
 * Used as a child of IntakeEntryLayout which provides the header and navigation.
 */
export const IntakeEntryMessagesRoute: FC = () => {
  const { [ROUTE_PARAMS.entryId]: entryId } = useParams() as { [ROUTE_PARAMS.entryId]: string };
  const workspace = useWorkspaceFromPath();
  const { data: entry, error, isLoading } = useGetEntry(workspace, entryId);

  if (isLoading) {
    return <Loading description="Loading conversation..." />;
  }

  if (error) {
    return (
      <StatusMessage
        className="mx-auto"
        size="medium"
        slotMedia={<ErrorIcon width={65} height={65} />}
        slotHeading="Error loading conversation"
        slotSubheading={error.message}
      />
    );
  }

  if (!entry) {
    return (
      <StatusMessage
        className="mx-auto"
        size="medium"
        slotHeading="Entry not found"
        slotSubheading="The requested entry could not be loaded."
      />
    );
  }

  return (
    <Flex className="overflow-hidden" gap="6">
      <IntakeEntryConversation
        entry={entry}
        attributes={{ Panel: { className: 'max-w-[66%] flex-2 overflow-y-auto' } }}
      />
      <IntakeAnnotationPanel
        entry={entry}
        attributes={{ Panel: { className: 'max-w-[33%] flex-1 overflow-y-auto' } }}
      />
    </Flex>
  );
};
