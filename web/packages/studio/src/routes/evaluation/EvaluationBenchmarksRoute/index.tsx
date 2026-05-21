// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEvaluationGetBenchmark } from '@nemo/sdk/generated/platform/api';
import { EvaluationBenchmarksDataView } from '@studio/components/dataViews/EvaluationBenchmarksDataView';
import type { BenchmarkItemWithId } from '@studio/components/dataViews/EvaluationBenchmarksDataView/types';
import { BenchmarkDetailsPanel } from '@studio/components/sidePanels/BenchmarkDetailsPanel';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import {
  getEvaluationBenchmarkDetailsRoute,
  getEvaluationBenchmarkListRoute,
} from '@studio/routes/utils';
import { type FC, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

export const EvaluationBenchmarksRoute: FC = () => {
  const workspace = useWorkspaceFromPath();
  const navigate = useNavigate();
  const { [ROUTE_PARAMS.benchmarkName]: benchmarkName } = useParams<{
    [ROUTE_PARAMS.benchmarkName]?: string;
  }>();

  const { data: benchmarkFromUrl, isPending: isBenchmarkDetailPending } = useEvaluationGetBenchmark(
    workspace,
    benchmarkName ?? '',
    { extended_response: true },
    {
      query: { enabled: !!benchmarkName },
    }
  );

  const handleRowClick = useCallback(
    (benchmark: BenchmarkItemWithId) => {
      if (!benchmark.name) return;
      navigate(getEvaluationBenchmarkDetailsRoute(workspace, benchmark.name), { replace: true });
    },
    [navigate, workspace]
  );

  const handlePanelClose = useCallback(
    (open: boolean) => {
      if (!open) navigate(getEvaluationBenchmarkListRoute(workspace), { replace: true });
    },
    [navigate, workspace]
  );

  return (
    <>
      <BenchmarkDetailsPanel
        benchmark={benchmarkFromUrl}
        isLoading={!!benchmarkName && isBenchmarkDetailPending}
        open={!!benchmarkName}
        onOpenChange={handlePanelClose}
      />
      <EvaluationBenchmarksDataView workspace={workspace} onRowClick={handleRowClick} />
    </>
  );
};
