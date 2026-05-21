// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useToast } from '@nemo/common/src/providers/toast/useToast';
import {
  getGetEntryQueryKey,
  getListEntriesQueryKey,
  useAddEvents,
} from '@nemo/sdk/generated/platform/api';
import { websiteLogger } from '@studio/util/logger';
import { useQueryClient } from '@tanstack/react-query';

interface Props {
  workspace: string;
  entryId?: string;
}
export const useCreateReviewerAnnotation = ({ workspace, entryId }: Props) => {
  const toast = useToast();
  const queryClient = useQueryClient();
  return useAddEvents({
    mutation: {
      onSuccess: () => {
        toast.success('Successfully added annotation!');
        queryClient.resetQueries({
          queryKey: entryId
            ? getGetEntryQueryKey(workspace, entryId)
            : getListEntriesQueryKey(workspace),
        });
      },
      onError: (error: Error) => {
        toast.error('Failed to add annotation. Please try again.');
        websiteLogger.error(error instanceof Error ? error.message : 'Failed to add events');
      },
    },
  });
};
