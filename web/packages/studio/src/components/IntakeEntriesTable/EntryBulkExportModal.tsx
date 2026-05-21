// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { zodResolver } from '@hookform/resolvers/zod';
import { useFilesetsInfinite } from '@nemo/common/src/api/entity-store/useDatasets';
import { ControlledCheckbox } from '@nemo/common/src/components/form/ControlledCheckbox';
import {
  ControlledSearchableSelect,
  SelectItemOption,
} from '@nemo/common/src/components/form/ControlledSearchableSelect';
import { ZodFormField } from '@nemo/common/src/components/form/ZodFormField';
import { FormModal } from '@nemo/common/src/components/FormModal';
import { getEntityReference } from '@nemo/common/src/namedEntity';
import { useToast } from '@nemo/common/src/providers/toast/useToast';
import { getListExportJobsQueryKey, useCreateExportJob } from '@nemo/sdk/generated/platform/api';
import { Entry } from '@nemo/sdk/generated/platform/schema';
import { Block, Button, Flex, Grid, GridItem, Stack, Text } from '@nvidia/foundations-react-core';
import { getDefaultExportFileName } from '@studio/components/form/NewExportJobForm/constants';
import { useWorkspaceFromPathIfExists } from '@studio/hooks/useWorkspaceFromPath';
import { handleFormErrorsGeneric } from '@studio/util/forms/error';
import { useBoolean } from '@studio/util/hooks/useBoolean';
import { websiteLogger } from '@studio/util/logger';
import { getTextWithCount } from '@studio/util/strings';
import { useQueryClient } from '@tanstack/react-query';
import { Database } from 'lucide-react';
import { FC, useCallback, useMemo } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { z } from 'zod';

// Form schema for bulk export
const exportRecordsFormSchema = z
  .object({
    dataset: z.object({
      name: z.string().min(1, 'Dataset is required'),
      files_url: z.string().optional(),
    }),
    config: z.object({
      limit: z
        .preprocess(
          (val) => (val === '' || val === undefined ? undefined : Number(val)),
          z.number().optional()
        )
        .describe('Maximum number of entries to export'),
      format_options: z
        .object({
          row_transformation: z.boolean().optional(),
        })
        .optional(),
    }),
  })
  .refine((data) => data.dataset.name && data.dataset.name.length > 0, {
    message: 'Dataset is required',
    path: ['dataset.name'],
  });

type ExportRecordsFormData = z.infer<typeof exportRecordsFormSchema>;

interface EntryBulkExportModalProps {
  /** Workspace identifier. Falls back to the `:workspace` route param when not provided. */
  workspace?: string;
  /** Entries to export */
  selectedEntries: Entry[];
  /** Callback when export succeeds */
  onSuccess: () => void;
  /** Whether to show a trigger button (default: true) */
  showTrigger?: boolean;
  /** Controlled open state (use with showTrigger=false) */
  open?: boolean;
  /** Callback when modal closes (use with showTrigger=false) */
  onClose?: () => void;
}

export const EntryBulkExportModal: FC<EntryBulkExportModalProps> = ({
  workspace: workspaceProp,
  selectedEntries,
  onSuccess,
  showTrigger = true,
  open: controlledOpen,
  onClose: controlledOnClose,
}) => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const routeWorkspace = useWorkspaceFromPathIfExists();
  const workspace = workspaceProp ?? routeWorkspace ?? '';
  const [internalOpen, openModal, closeModalInternal] = useBoolean(false);

  // Support both controlled and uncontrolled modes
  const isOpen = showTrigger ? internalOpen : (controlledOpen ?? false);
  const closeModal = useMemo(
    () => (showTrigger ? closeModalInternal : (controlledOnClose ?? (() => {}))),
    [showTrigger, closeModalInternal, controlledOnClose]
  );

  const { mutateAsync: createExportJob, isPending: isCreatingExportJob } = useCreateExportJob();

  const form = useForm<ExportRecordsFormData>({
    resolver: zodResolver(exportRecordsFormSchema),
    defaultValues: {
      dataset: { name: '', files_url: '' },
      config: { limit: 1000 },
    },
  });

  const { control, setValue, watch } = form;
  const datasetName = watch('dataset.name');

  // Query datasets for the select dropdown
  const {
    data: datasetsPages,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useFilesetsInfinite({
    query: {
      sort: '-created_at',
      filter: { purpose: 'dataset' },
    },
    workspace,
  });

  // Flatten all pages into a single array of options
  const datasetOptions: SelectItemOption[] = useMemo(() => {
    const allDatasets = datasetsPages?.pages.flatMap((page) => page.data) ?? [];
    return allDatasets.map((dataset) => ({
      value: dataset.name ?? '',
      label: dataset.name ?? '',
    }));
  }, [datasetsPages]);

  const handleLoadMore = useCallback(async () => {
    if (hasNextPage && !isFetchingNextPage) {
      await fetchNextPage();
    }
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

  const resetAndClose = useCallback(() => {
    closeModal();
    form.reset();
  }, [closeModal, form]);

  const submitForm = async (data: ExportRecordsFormData) => {
    try {
      // Build the export job request with selected entry IDs
      const entryIds = selectedEntries.map((entry) => entry.id).filter(Boolean) as string[];

      // Generate export file name
      const exportFileName = getDefaultExportFileName();

      // Construct output_file_url from dataset.files_url + export_file_name
      const outputFileUrl = data.dataset.files_url
        ? `${data.dataset.files_url}/${exportFileName}`
        : undefined;

      if (!outputFileUrl) {
        toast.error('Dataset files URL is required. Please select a valid dataset.');
        return;
      }

      await createExportJob({
        workspace,
        data: {
          output_file_url: outputFileUrl,
          config: {
            limit: data.config.limit,
            filters: {
              id: { in: entryIds },
            },
            format_options: data.config.format_options,
          },
        },
      });

      resetAndClose();
      toast.success('Export job created successfully!');
      queryClient.resetQueries({ queryKey: getListExportJobsQueryKey(workspace) });
      onSuccess();
    } catch (error) {
      websiteLogger.error(error instanceof Error ? error.message : 'Failed to create export job');
      toast.error('Failed to create export job. Please try again.');
    }
  };

  const entryCount = selectedEntries.length;

  return (
    <>
      {showTrigger && (
        <Button kind="tertiary" onClick={openModal} data-testid="entry-bulk-export-modal-trigger">
          <Database />
          Export to Dataset
        </Button>
      )}

      <FormModal
        open={isOpen}
        className="w-auto min-w-[500px] max-w-[600px]"
        title="Export Records to Dataset"
        submitButtonText="Confirm"
        disabled={isCreatingExportJob}
        loading={isCreatingExportJob}
        submitDisabled={!datasetName}
        onSubmit={form.handleSubmit(
          submitForm,
          handleFormErrorsGeneric({ title: 'Export Records Form Errors' })
        )}
        onClose={resetAndClose}
      >
        <FormProvider {...form}>
          <Stack gap="6" className="overflow-auto">
            <Text kind="body/regular/md">
              Export selected entries to a Dataset for downstream training or evaluation.
            </Text>

            <ControlledSearchableSelect
              options={datasetOptions}
              onLoadMore={handleLoadMore}
              onChange={(value) => {
                const datasets = datasetsPages?.pages.flatMap((page) => page.data) ?? [];
                const foundDataset = datasets.find((dataset) => dataset.name === value);
                if (foundDataset) {
                  setValue('dataset.files_url', getEntityReference(foundDataset) ?? '');
                }
              }}
              hasMore={hasNextPage ?? false}
              isLoading={isLoading}
              isLoadingMore={isFetchingNextPage}
              searchPlaceholder="Search datasets..."
              triggerPlaceholder="No Dataset Selected"
              emptyMessage="No datasets found"
              doneLoadingMessage="All datasets loaded"
              renderValue={(value) =>
                value ? (
                  <Flex align="center" gap="2">
                    <Database className="flex-none" />
                    <Text kind="body/regular/md">{value}</Text>
                  </Flex>
                ) : null
              }
              formFieldProps={{ slotLabel: 'Destination Dataset' }}
              useControllerProps={{ name: 'dataset.name', control }}
            />

            <Grid cols={2}>
              <GridItem>
                <ZodFormField
                  schema={z
                    .preprocess(
                      (val) => (val === '' || val === undefined ? undefined : Number(val)),
                      z.number().optional()
                    )
                    .describe('Maximum number of records to export')}
                  useControllerProps={{ name: 'config.limit', control }}
                  formFieldProps={{
                    slotLabel: 'Limit',
                    slotInfo: 'Maximum number of records to export',
                  }}
                />
              </GridItem>
            </Grid>

            <ControlledCheckbox
              slotLabel="Use annotation rewrites (when available)"
              formFieldProps={{ slotLabel: 'Row Transformation' }}
              useControllerProps={{ name: 'config.format_options.row_transformation', control }}
            />

            {/* Info panel showing selection count */}
            <Block className="bg-surface-raised rounded-lg p-6">
              <Text kind="body/regular/md">
                {getTextWithCount('entry', entryCount, 'entries')} will be exported
              </Text>
            </Block>
          </Stack>
        </FormProvider>
      </FormModal>
    </>
  );
};
