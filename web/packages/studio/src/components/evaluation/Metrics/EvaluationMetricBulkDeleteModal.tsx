// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEvaluationDeleteMetric } from '@nemo/sdk/generated/platform/api';
import { Button } from '@nvidia/foundations-react-core';
import { useMutateMany } from '@studio/api/common/useMutateMany';
import { DeleteConfirmationModal } from '@studio/components/DeleteConfirmationModal';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { getTextWithCount } from '@studio/util/strings';
import { Trash } from 'lucide-react';
import { FC, useState } from 'react';

interface EvaluationMetricBulkDeleteModalProps {
  selectedMetrics: { name?: string }[];
  onConfirmSuccess: () => void;
}

export const EvaluationMetricBulkDeleteModal: FC<EvaluationMetricBulkDeleteModalProps> = ({
  selectedMetrics,
  onConfirmSuccess,
}) => {
  const [open, setOpen] = useState<boolean>(false);
  const workspace = useWorkspaceFromPath();

  const { mutateAsync: deleteMetric } = useEvaluationDeleteMetric();
  const { mutateAsync: deleteMetrics } = useMutateMany(deleteMetric);

  const validMetrics = selectedMetrics.filter((m) => !!m.name) as { name: string }[];
  const metricCountLabel = getTextWithCount('metric', validMetrics.length);

  const handleDelete = async () => {
    try {
      await deleteMetrics(validMetrics.map(({ name }) => ({ workspace, name })));
      onConfirmSuccess();
      return true;
    } catch (error) {
      console.error('Failed to delete evaluation metrics:', error);
      return false;
    }
  };

  return (
    <>
      <Button
        kind="secondary"
        data-testid="bulk-delete-modal-trigger-button"
        disabled={validMetrics.length === 0}
        onClick={() => setOpen(true)}
      >
        <Trash />
        Delete
      </Button>
      <DeleteConfirmationModal
        open={open}
        onClose={() => setOpen(false)}
        onDelete={handleDelete}
        title={`Delete ${getTextWithCount('Metric', validMetrics.length)}`}
        description={`Are you sure you want to delete ${metricCountLabel}? This action cannot be undone.`}
        simpleConfirm
        successText={`Successfully deleted ${getTextWithCount('evaluation metric', validMetrics.length)}`}
        errorText="Failed to delete evaluation metrics. Please try again."
      />
    </>
  );
};
