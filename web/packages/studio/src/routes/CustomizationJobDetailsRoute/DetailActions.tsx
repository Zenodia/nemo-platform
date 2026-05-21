// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { LoadingButton } from '@nemo/common/src/components/LoadingButton';
import { CJobCancellableStatuses, CJobLaunchableStatuses } from '@nemo/common/src/constants/query';
import { useToast } from '@nemo/common/src/providers/toast/useToast';
import { PlatformJobStatus } from '@nemo/sdk/generated/platform/schema';
import {
  getCustomizationGetJobQueryKey,
  CustomizationGetJobQueryResult,
  useCustomizationCancelJob,
} from '@nemo/sdk/vendored/customizer/api';
import { Button } from '@nvidia/foundations-react-core';
import { getErrorMessage } from '@studio/api/common/utils';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { getNewEvaluationMetricRoute } from '@studio/routes/utils';
import { useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { FC } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

interface DetailActionsProps {
  model?: string;
  status?: PlatformJobStatus;
}

/**
 * This component renders the primary top-level CTAs for the customization job details page.
 */
export const DetailActions: FC<DetailActionsProps> = ({ model, status }) => {
  const toast = useToast();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const workspace = useWorkspaceFromPath();
  const { [ROUTE_PARAMS.customizationJobId]: jobId } = useParams();
  const { mutateAsync, isPending } = useCustomizationCancelJob({
    mutation: {
      onSuccess: () => {
        toast.success('Job cancelled successfully.');
        if (jobId) {
          // Optimistically update the job status to cancelled
          queryClient.setQueryData(
            getCustomizationGetJobQueryKey(workspace, jobId),
            (oldData: CustomizationGetJobQueryResult | undefined) => {
              if (!oldData) return oldData;
              return {
                ...oldData,
                status: PlatformJobStatus.cancelled,
              };
            }
          );
        }
      },
    },
  });

  const cancelJob = async () => {
    if (!jobId) {
      toast.error('Job ID is required');
      return;
    }
    try {
      await mutateAsync({ workspace, name: jobId });
    } catch (e) {
      if (e instanceof AxiosError || e instanceof Error) {
        toast.error(`Failed to cancel job: ${getErrorMessage(e)}`);
      } else {
        toast.error('Failed to cancel job: Unknown error');
      }
    }
  };

  const disabled = isPending || !jobId;
  if (isPending || status === PlatformJobStatus.cancelling) {
    return (
      <LoadingButton kind="secondary" loading disabled>
        Cancelling...
      </LoadingButton>
    );
  } else if (status && CJobCancellableStatuses.includes(status)) {
    return (
      <Button kind="secondary" onClick={cancelJob} disabled={disabled}>
        Cancel Job
      </Button>
    );
  } else if (status && CJobLaunchableStatuses.includes(status)) {
    return (
      <Button
        color="brand"
        disabled={disabled}
        onClick={() => {
          navigate(getNewEvaluationMetricRoute(workspace, { model }));
        }}
      >
        Evaluate
      </Button>
    );
  }
};
