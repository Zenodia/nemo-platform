// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { zodResolver } from '@hookform/resolvers/zod';
import { ErrorMessage } from '@nemo/common/src/components/ErrorMessage';
import { ControlledTextInput } from '@nemo/common/src/components/form/ControlledTextInput';
import { LoadingButton } from '@nemo/common/src/components/LoadingButton';
import { useDataDesignerCreateJob } from '@nemo/sdk/generated/data-designer/api';
import type { CreateJobRequest as DataDesignerJobRequest } from '@nemo/sdk/generated/data-designer/schema';
import { useModelsListProviders } from '@nemo/sdk/generated/platform/api';
import {
  Button,
  CodeSnippet,
  Divider,
  Flex,
  Grid,
  Panel,
  Stack,
  Text,
} from '@nvidia/foundations-react-core';
import { JobRequestGenerator } from '@studio/components/NewDataDesignerJobForm/JobRequestGenerator';
import { formatPreviewLogsForDisplay } from '@studio/components/NewDataDesignerJobForm/previewApi';
import { usePreview } from '@studio/components/NewDataDesignerJobForm/usePreview';
import {
  type DataDesignerModelOption,
  modelsFromProviders,
  sanitizeJobRequestName,
} from '@studio/components/NewDataDesignerJobForm/utils';
import { DEFAULT_BUILD_MODEL_NAME, DEFAULT_LARGE_PAGE_SIZE } from '@studio/constants/constants';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import {
  getDataDesignerJobDetailsRoute,
  getDataDesignerJobListRoute,
  getWorkspaceInferenceProvidersRoute,
} from '@studio/routes/utils';
import { type FC, useCallback, useMemo, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from 'react-oidc-context';
import { Link, useNavigate } from 'react-router-dom';
import { z } from 'zod';

export type { DataDesignerModelOption };

const newDataDesignerJobFormSchema = z.object({
  name: z
    .string()
    .refine(
      (val) => !val || !/\s/.test(val),
      'Name must not contain spaces. Use hyphens or underscores (e.g. my-data-job).'
    ),
  jobDescription: z.string(),
  description: z
    .string()
    .min(1, 'Description is required')
    .min(
      10,
      'Please provide at least a short description (e.g. "100 rows of product reviews with sentiment")'
    ),
  modelRef: z.string().min(1, 'Please select a model'),
  rows: z.number({ required_error: 'Rows is required' }).min(1, 'Must be at least 1'),
  inferenceSecret: z.string().optional(),
});

export type NewDataDesignerJobFormFields = z.infer<typeof newDataDesignerJobFormSchema>;

export const NewDataDesignerJobForm: FC = () => {
  const workspace = useWorkspaceFromPath();
  const navigate = useNavigate();
  const { user } = useAuth();

  const modelRef = `${workspace}/${DEFAULT_BUILD_MODEL_NAME}`;

  const { control, handleSubmit, setValue } = useForm<NewDataDesignerJobFormFields>({
    resolver: zodResolver(newDataDesignerJobFormSchema),
    defaultValues: {
      name: '',
      jobDescription: '',
      description: '',
      modelRef,
      rows: 100,
    },
  });

  const { data: providersPage, isLoading: isLoadingModels } = useModelsListProviders(
    workspace,
    { page_size: DEFAULT_LARGE_PAGE_SIZE },
    { query: {} }
  );
  const models = useMemo(
    () => modelsFromProviders(providersPage?.data ?? []),
    [providersPage?.data]
  );
  const selectedModel = models?.find((m) => m.id === modelRef);
  const modelNotFound = !isLoadingModels && !selectedModel;

  const [jobRequest, setJobRequest] = useState<DataDesignerJobRequest | null>(null);
  const jobRequestRef = useRef<DataDesignerJobRequest | null>(null);
  jobRequestRef.current = jobRequest; // keep ref in sync so usePreview's getCurrentConfig() sees latest

  const handleJobRequestChange = useCallback(
    (next: DataDesignerJobRequest | null) => {
      jobRequestRef.current = next;
      setJobRequest(next);
      if (next?.spec?.num_records != null) {
        setValue('rows', next.spec.num_records);
      }
    },
    [setValue]
  );

  const getCurrentConfig = useCallback(() => jobRequestRef.current?.spec?.config, []);
  const { previewLogs, isPreviewing, runPreview } = usePreview({
    workspace,
    accessToken: user?.access_token ?? undefined,
    getCurrentConfig,
  });

  const createJob = useDataDesignerCreateJob();
  const isSubmitting = createJob.isPending;
  const submitError = createJob.error instanceof Error ? createJob.error.message : null;

  const onSubmit = useCallback(
    async (fields: NewDataDesignerJobFormFields) => {
      const current = jobRequestRef.current;
      if (!current?.spec?.config) return;

      const fromSpec = current.spec.num_records;
      const fromForm = Number(fields.rows);
      const numRecords = fromForm || fromSpec || 10;
      const merged: DataDesignerJobRequest = {
        ...current,
        spec: { ...current.spec, num_records: numRecords },
      };
      if (fields.name.trim()) merged.name = fields.name.trim();
      if (fields.jobDescription.trim()) merged.description = fields.jobDescription.trim();
      const toSubmit = sanitizeJobRequestName(merged);

      try {
        const created = await createJob.mutateAsync({ workspace, data: toSubmit });
        if (created?.name) {
          navigate(getDataDesignerJobDetailsRoute(workspace, created.name));
        } else {
          navigate(getDataDesignerJobListRoute(workspace));
        }
      } catch {
        // Error surfaced via createJob.error
      }
    },
    [workspace, createJob, navigate]
  );

  if (modelNotFound) {
    return (
      <Panel elevation="high" density="standard">
        <ErrorMessage
          header="Model Not Available"
          message={
            <>
              Add the{' '}
              <Link
                to={getWorkspaceInferenceProvidersRoute(workspace, { preset: 'build' })}
                className="underline"
              >
                NVIDIA Build Inference Provider
              </Link>{' '}
              to your Workspace to enable this feature.
            </>
          }
          slotFooter={
            <Button
              kind="secondary"
              onClick={() =>
                navigate(getWorkspaceInferenceProvidersRoute(workspace, { preset: 'build' }))
              }
            >
              Go to Inference Providers
            </Button>
          }
          height="auto"
        />
      </Panel>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Stack gap="density-2xl">
        <Panel
          elevation="high"
          density="standard"
          slotFooter={
            <Flex className="w-full justify-between">
              <Button
                type="button"
                kind="secondary"
                onClick={() => navigate(getDataDesignerJobListRoute(workspace))}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Flex gap="density-md">
                <LoadingButton
                  type="button"
                  kind="secondary"
                  onClick={runPreview}
                  loading={isPreviewing}
                >
                  Preview
                </LoadingButton>
                <LoadingButton type="submit" color="brand" loading={isSubmitting}>
                  Create Job
                </LoadingButton>
              </Flex>
            </Flex>
          }
        >
          <Stack gap="density-2xl">
            {/* Job Details */}
            <Flex gap="density-2xl" align="start">
              <Stack className="w-2/5 shrink-0" gap="density-xs">
                <Text kind="label/bold/lg">Job Details</Text>
                <Text kind="body/regular/sm">
                  Give this job a name and description to identify it later.
                </Text>
              </Stack>
              <Stack className="flex-1" gap="density-md">
                <Grid cols={2} gap="density-md">
                  <ControlledTextInput
                    label="Name (optional)"
                    formFieldProps={{
                      slotHelp:
                        'No spaces — use hyphens or underscores. Overrides the name from the generated config.',
                    }}
                    useControllerProps={{ name: 'name', control }}
                  />
                  <ControlledTextInput
                    label="Description (optional)"
                    useControllerProps={{
                      name: 'jobDescription',
                      control,
                    }}
                  />
                </Grid>
              </Stack>
            </Flex>

            <Divider />

            {/* Configuration */}
            <Flex gap="density-2xl" align="start">
              <Stack className="w-2/5 shrink-0" gap="density-xs">
                <Text kind="label/bold/lg">Configuration</Text>
                <Text kind="body/regular/sm">Set the number of records to produce.</Text>
              </Stack>
              <Stack className="flex-1" gap="density-md">
                <ControlledTextInput
                  label="Rows"
                  type="number"
                  min={1}
                  step={1}
                  required
                  formFieldProps={{
                    slotHelp: 'Number of records to generate.',
                  }}
                  useControllerProps={{
                    name: 'rows',
                    control,
                  }}
                />
              </Stack>
            </Flex>

            <Divider />

            {/* Data Specification */}
            <Stack gap="density-lg">
              <Stack gap="density-xs">
                <Text kind="label/bold/lg">Data Specification</Text>
                <Text kind="body/regular/sm">
                  Describe the type of data you want to generate. The selected model will convert
                  this into a job specification, which you can review and edit before submitting.
                </Text>
              </Stack>
              <JobRequestGenerator
                workspace={workspace}
                modelRef={modelRef}
                provider={selectedModel?.model_providers?.[0] ?? ''}
                servedModelName={selectedModel?.served_model_name ?? ''}
                control={control}
                descriptionName="description"
                onJobRequestChange={handleJobRequestChange}
                disabled={isPreviewing || isSubmitting}
              />
            </Stack>
          </Stack>
        </Panel>

        {submitError && (
          <Text kind="body/regular/sm" className="text-danger">
            {submitError}
          </Text>
        )}

        <CodeSnippet
          value={
            previewLogs ? formatPreviewLogsForDisplay(previewLogs) : 'Run Preview to see logs.'
          }
          language="json"
          kind="block"
          attributes={{ CodeSnippetCode: { className: 'max-h-[600px]' } }}
        />
      </Stack>
    </form>
  );
};
