// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { LoadingButton } from '@nemo/common/src/components/LoadingButton';
import { useToast } from '@nemo/common/src/providers/toast/useToast';
import { useDeleteEntry } from '@nemo/sdk/generated/platform/api';
import { Entry } from '@nemo/sdk/generated/platform/schema';
import { Button, Flex, Modal } from '@nvidia/foundations-react-core';
import { useMutateMany } from '@studio/api/common/useMutateMany';
import { websiteLogger } from '@studio/util/logger';
import { getTextWithCount } from '@studio/util/strings';
import { useQueryClient } from '@tanstack/react-query';
import { Trash } from 'lucide-react';
import { FC, useState } from 'react';

interface EntryBulkDeleteModalProps {
  workspace: string;
  selectedEntries: Entry[];
  onConfirmSuccess: () => void;
}

export const EntryBulkDeleteModal: FC<EntryBulkDeleteModalProps> = ({
  workspace,
  selectedEntries,
  onConfirmSuccess,
}) => {
  const [open, setOpen] = useState<boolean>(false);
  const toast = useToast();
  const queryClient = useQueryClient();

  const { mutateAsync: deleteEntry } = useDeleteEntry();
  const { mutateAsync: deleteEntries, isPending } = useMutateMany(deleteEntry);

  const handleDelete = async () => {
    try {
      const entriesToDelete = selectedEntries.filter((entry) => entry.id);

      await deleteEntries(entriesToDelete.map((entry) => ({ workspace, name: entry.id! })));

      const count = entriesToDelete.length;
      toast.success(`Successfully deleted ${getTextWithCount('entry', count, 'entries')}`);

      queryClient.invalidateQueries({
        queryKey: [`/apis/intake/v2/workspaces/${workspace}/entries`],
      });

      onConfirmSuccess();
      setOpen(false);
    } catch (error) {
      websiteLogger.error(error instanceof Error ? error.message : 'Failed to delete entries');
      toast.error('Failed to delete entries. Please try again.');
    }
  };

  const handleOpenChange = (shouldOpen: boolean) => {
    if (!isPending) {
      setOpen(shouldOpen);
    }
  };

  const entryCount = selectedEntries.length;

  return (
    <Modal
      open={open}
      onOpenChange={handleOpenChange}
      slotTrigger={
        <Button kind="tertiary" data-testid="bulk-delete-modal-trigger-button">
          <Trash />
          Delete
        </Button>
      }
      slotHeading={
        <>
          <Trash />
          Delete {getTextWithCount('Entry', entryCount, 'Entries')}
        </>
      }
      slotFooter={
        <Flex justify="end" gap="density-xs" align="center" className="w-full">
          <Button
            onClick={() => setOpen(false)}
            kind="tertiary"
            color="neutral"
            disabled={isPending}
          >
            Cancel
          </Button>
          <LoadingButton onClick={handleDelete} loading={isPending}>
            Delete
          </LoadingButton>
        </Flex>
      }
    >
      Are you sure you want to delete {getTextWithCount('entry', entryCount, 'entries')}? This
      action cannot be undone.
    </Modal>
  );
};
