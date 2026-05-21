// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getEntityReference, getURNFromNamedEntityRef } from '@nemo/common/src/namedEntity';
import { useToast } from '@nemo/common/src/providers/toast/useToast';
import { ResizeablePanel } from '@studio/components/common/ResizeablePanel';
import { MetricDetailsPanel } from '@studio/components/evaluation/Jobs/form/MetricDetailsPanel';
import { MetricLLMJudgePanel } from '@studio/components/evaluation/Jobs/form/MetricLLMJudgePanel';
import { ConfirmationModal } from '@studio/components/modals/ConfirmationModal';
import { DEFAULT_BUILD_MODEL_NAME } from '@studio/constants/constants';
import { useJudgeModels } from '@studio/hooks/evaluation/useJudgeModels';
import {
  type MetricPanelFormData,
  useMetricPanelForm,
} from '@studio/hooks/evaluation/useMetricPanelForm';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { handleFormErrorsGeneric } from '@studio/util/forms/error';
import { type FC, useEffect, useMemo, useRef, useState } from 'react';
import { type FieldErrors, FormProvider } from 'react-hook-form';

async function resolveSubmitSuccess(
  result: boolean | Promise<boolean> | void | Promise<void>
): Promise<boolean> {
  const settled = await result;
  return settled !== false;
}

interface MetricFormPanelsProps {
  /** Return false when the save failed after showing your own error UI; otherwise return true or void. */
  onSubmit: (data: MetricPanelFormData) => boolean | Promise<boolean> | void | Promise<void>;
  formId?: string;
}

export const MetricFormPanels: FC<MetricFormPanelsProps> = ({ onSubmit, formId }) => {
  const form = useMetricPanelForm();
  const workspace = useWorkspaceFromPath();
  const { data: judgeModels = [], isLoading: judgeModelsLoading } = useJudgeModels({
    enabled: !!workspace,
  });
  const defaultJudgeModelUrn = useMemo(() => {
    if (!workspace) return '';
    const candidate = getEntityReference({ workspace, name: DEFAULT_BUILD_MODEL_NAME });
    return judgeModels.some((m) => getURNFromNamedEntityRef(m) === candidate) ? candidate : '';
  }, [workspace, judgeModels]);

  const defaultJudgeModelAppliedRef = useRef(false);
  const toast = useToast();
  const [hasSuccessfulTestRun, setHasSuccessfulTestRun] = useState(false);
  const [saveWithoutTestOpen, setSaveWithoutTestOpen] = useState(false);
  const [pendingSubmitData, setPendingSubmitData] = useState<MetricPanelFormData | null>(null);

  const { handleSubmit, watch, getValues, setValue } = form;

  useEffect(() => {
    if (judgeModelsLoading || !defaultJudgeModelUrn || defaultJudgeModelAppliedRef.current) {
      return;
    }
    const currentName = getValues('body.model.name');
    if (!currentName) {
      setValue('body.model.name', defaultJudgeModelUrn, {
        shouldDirty: false,
        shouldValidate: true,
      });
      defaultJudgeModelAppliedRef.current = true;
    }
  }, [judgeModelsLoading, defaultJudgeModelUrn, getValues, setValue]);

  useEffect(() => {
    const subscription = watch(() => {
      setHasSuccessfulTestRun(false);
    });
    return () => subscription.unsubscribe();
  }, [watch]);

  const onError = (errors: FieldErrors) => {
    toast.error(
      'There was an error with the form submission. Please fix any errors and try again.'
    );
    handleFormErrorsGeneric({ title: 'Evaluation Metric' })(errors);
  };

  const flushSubmit = async (data: MetricPanelFormData) => resolveSubmitSuccess(onSubmit(data));

  const trySubmit = (data: MetricPanelFormData) => {
    if (!hasSuccessfulTestRun) {
      setPendingSubmitData(data);
      setSaveWithoutTestOpen(true);
      return;
    }
    void flushSubmit(data);
  };

  return (
    <>
      <FormProvider {...form}>
        <form
          id={formId}
          onSubmit={handleSubmit(trySubmit, onError)}
          className="flex flex-col gap-4 h-full w-full relative"
        >
          <ResizeablePanel
            className="flex-1 min-h-0"
            leftClassName="p-6"
            rightClassName="p-6 flex flex-col gap-10"
            slotLeft={<MetricDetailsPanel />}
            slotRight={
              <MetricLLMJudgePanel onSuccessfulTestRun={() => setHasSuccessfulTestRun(true)} />
            }
          />
        </form>
      </FormProvider>
      <ConfirmationModal
        open={saveWithoutTestOpen}
        onClose={() => {
          setSaveWithoutTestOpen(false);
          setPendingSubmitData(null);
        }}
        title="Save without Testing?"
        description="You have not run a successful test from the Test tab. You can still save this metric; run a test first if you want to preview results with your sample data."
        submitButtonText="Save"
        onConfirm={async () => {
          if (!pendingSubmitData) return false;
          return flushSubmit(pendingSubmitData);
        }}
        suppressResultToasts
      />
    </>
  );
};
