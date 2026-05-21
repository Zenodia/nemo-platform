// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Button, ButtonProps } from '@nvidia/foundations-react-core';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { getEvaluationMetricRunRoute, getEvaluationMetricsRunRoute } from '@studio/routes/utils';
import { useNavigate } from 'react-router-dom';

type ButtonLaunchEvaluationProps = ButtonProps & {
  /** Optional metric reference (namespace/name) to pre-fill in the form */
  metricRef?: string;
  /** Optional model reference to pre-fill in the metric run side panel */
  modelRef?: string;
};

/**
 * Button that navigates to the evaluation launch form.
 * Optionally accepts a metricRef and modelRef to pre-fill the run side panel.
 */
export const ButtonLaunchEvaluation = ({
  metricRef,
  modelRef,
  children = 'Launch Evaluation',
  ...buttonProps
}: ButtonLaunchEvaluationProps) => {
  const navigate = useNavigate();
  const workspace = useWorkspaceFromPath();

  const handleLaunchEvaluationsClick = () => {
    if (metricRef) {
      navigate(getEvaluationMetricRunRoute(workspace, metricRef, { model: modelRef }));
    } else {
      navigate(getEvaluationMetricsRunRoute(workspace, { model: modelRef }));
    }
  };

  return (
    <Button
      color="brand"
      {...buttonProps}
      onClick={handleLaunchEvaluationsClick}
      data-testid="button-launch-evaluation"
    >
      {children}
    </Button>
  );
};
