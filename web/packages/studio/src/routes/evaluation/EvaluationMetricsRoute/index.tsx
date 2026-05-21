// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEvaluationGetMetric } from '@nemo/sdk/generated/platform/api';
import { EvaluationMetricsDataView } from '@studio/components/dataViews/EvaluationMetricsDataView';
import type { MetricItemWithId } from '@studio/components/dataViews/EvaluationMetricsDataView/types';
import { MetricDetailsPanel } from '@studio/components/sidePanels/MetricDetailsPanel';
import { MetricRunSidePanel } from '@studio/components/sidePanels/MetricRunSidePanel';
import { ROUTE_PARAMS, ROUTES } from '@studio/constants/routes';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { getEvaluationMetricDetailsRoute, getEvaluationMetricsRoute } from '@studio/routes/utils';
import { type FC, useCallback } from 'react';
import { useMatch, useNavigate, useParams } from 'react-router-dom';

export const EvaluationMetricsRoute: FC = () => {
  const workspace = useWorkspaceFromPath();
  const navigate = useNavigate();
  const { [ROUTE_PARAMS.evaluationJobId]: metricId } = useParams<{
    [ROUTE_PARAMS.evaluationJobId]?: string;
  }>();

  const isMetricRunRoute = useMatch(ROUTES.workspace.evaluationMetricRun);
  const isMetricsRunRoute = useMatch(ROUTES.workspace.evaluationMetricsRun);
  const isRunMode = !!(isMetricRunRoute || isMetricsRunRoute);

  const { data: metricFromUrl } = useEvaluationGetMetric(workspace, metricId ?? '', {
    query: { enabled: !!metricId },
  });

  const handleRowClick = useCallback(
    (metric: MetricItemWithId) => {
      if (!metric.name) return;
      navigate(getEvaluationMetricDetailsRoute(workspace, metric.name), { replace: true });
    },
    [navigate, workspace]
  );

  const handleDetailsPanelClose = useCallback(
    (open: boolean) => {
      if (!open) navigate(getEvaluationMetricsRoute(workspace), { replace: true });
    },
    [navigate, workspace]
  );

  const handleRunPanelClose = useCallback(
    (open: boolean) => {
      if (!open) {
        navigate(getEvaluationMetricsRoute(workspace), { replace: true });
      }
    },
    [navigate, workspace]
  );

  return (
    <>
      <MetricRunSidePanel
        metric={(metricFromUrl as MetricItemWithId | undefined) ?? null}
        open={isRunMode}
        onOpenChange={handleRunPanelClose}
        workspace={workspace}
      />
      <MetricDetailsPanel
        metric={metricFromUrl}
        open={!!metricId && !isRunMode}
        onOpenChange={handleDetailsPanelClose}
      />
      <EvaluationMetricsDataView workspace={workspace} onRowClick={handleRowClick} />
    </>
  );
};
