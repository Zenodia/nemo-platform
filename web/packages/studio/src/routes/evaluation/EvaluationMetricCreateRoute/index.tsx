// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { LoadingButton } from '@nemo/common/src/components/LoadingButton';
import { useToast } from '@nemo/common/src/providers/toast/useToast';
import { useEvaluationCreateMetric } from '@nemo/sdk/generated/platform/api';
import { PageHeader, Stack } from '@nvidia/foundations-react-core';
import { getErrorMessage, isValidationErrorArray } from '@studio/api/common/utils';
import { AccessibleTitle } from '@studio/components/AccessibleTitle';
import { MetricFormPanels } from '@studio/components/evaluation/Jobs/form/MetricFormPanels';
import { buildLLMJudgeChatPromptTemplate } from '@studio/components/evaluation/Jobs/form/utils';
import { cleanScoresObj } from '@studio/components/evaluation/Jobs/TestMetric/utils';
import type { MetricPanelFormData } from '@studio/hooks/evaluation/useMetricPanelForm';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { useBreadcrumbs } from '@studio/providers/breadcrumbs/useBreadcrumbs';
import { getEvaluationMetricsRoute } from '@studio/routes/utils';
import { websiteLogger } from '@studio/util/logger';
import { type FC } from 'react';
import { useNavigate } from 'react-router-dom';

export const EvaluationMetricCreateRoute: FC = () => {
  const workspace = useWorkspaceFromPath();
  const navigate = useNavigate();
  const toast = useToast();

  const { mutateAsync: createMetric, isPending } = useEvaluationCreateMetric();

  useBreadcrumbs({
    items: [
      {
        href: getEvaluationMetricsRoute(workspace),
        slotLabel: 'Metrics',
      },
      {
        slotLabel: 'New',
      },
    ],
  });

  const handleSubmit = async (data: MetricPanelFormData): Promise<boolean> => {
    try {
      const scores = cleanScoresObj(data.body.scores);
      const promptTemplate = buildLLMJudgeChatPromptTemplate(data.body.messages);

      const body: Record<string, unknown> = {
        type: 'llm-judge',
        model: data.body.model.name,
        scores,
      };
      if (data.body.description) body.description = data.body.description;
      if (promptTemplate) body.prompt_template = promptTemplate;
      if (data.body.inference && Object.keys(data.body.inference).length > 0) {
        body.inference = data.body.inference;
      }

      await createMetric({ workspace, name: data.name, data: body });

      toast.success('Evaluation metric created successfully');
      navigate(getEvaluationMetricsRoute(workspace));
      return true;
    } catch (error) {
      const detail = (error as { response?: { data?: { detail?: unknown } } }).response?.data
        ?.detail;

      if (isValidationErrorArray(detail)) {
        toast.error('Please fix the validation errors shown in the form.');
        return false;
      }

      const message = getErrorMessage(error as Error, 'Failed to create evaluation metric');
      websiteLogger.error(`Form submission error: ${message}`);
      toast.error(message);
      return false;
    }
  };

  return (
    <AccessibleTitle title={`Create evaluation metric for ${workspace}`}>
      <Stack gap="density-2xl" padding="density-2xl" className="h-full overflow-hidden">
        <PageHeader
          className="p-0 shrink-0"
          slotHeading="New Evaluation Metric"
          slotDescription="A reusable evaluation component that defines how to score model outputs."
          slotActions={
            <LoadingButton type="submit" form="metric-form" loading={isPending} color="brand">
              Save Evaluation Metric
            </LoadingButton>
          }
        />
        <div className="flex-1 min-h-0">
          <MetricFormPanels onSubmit={handleSubmit} formId="metric-form" />
        </div>
      </Stack>
    </AccessibleTitle>
  );
};
