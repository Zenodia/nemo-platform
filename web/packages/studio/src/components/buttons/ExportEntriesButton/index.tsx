// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { zodResolver } from '@hookform/resolvers/zod';
import { FormModal } from '@nemo/common/src/components/FormModal';
import { useToast } from '@nemo/common/src/providers/toast/useToast';
import { getListExportJobsQueryKey, useCreateExportJob } from '@nemo/sdk/generated/platform/api';
import { Button } from '@nvidia/foundations-react-core';
import { NewExportJobForm } from '@studio/components/form/NewExportJobForm';
import {
  getDefaultExportFileName,
  newExportJobFormSchema,
} from '@studio/components/form/NewExportJobForm/constants';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { handleFormErrorsGeneric } from '@studio/util/forms/error';
import { useBoolean } from '@studio/util/hooks/useBoolean';
import { websiteLogger } from '@studio/util/logger';
import { useQueryClient } from '@tanstack/react-query';
import { FormProvider, useForm } from 'react-hook-form';
import { z } from 'zod';

/**
 * A button that enacapsulates the logic for rendering a Form Modal to export entries to a dataset.
 * @returns
 */
export const ExportEntriesButton = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const workspace = useWorkspaceFromPath();
  const [isOpen, openModal, closeModal] = useBoolean(false);
  const { mutateAsync: createExportJob, isPending: isCreatingExportJob } = useCreateExportJob();
  const form = useForm<z.infer<typeof newExportJobFormSchema>>({
    resolver: zodResolver(newExportJobFormSchema),
    defaultValues: {
      export_file_name: getDefaultExportFileName(),
      namespace: workspace,
      config: { limit: 1000 },
    },
  });

  const resetAndClose = () => {
    closeModal();
    form.reset();
  };

  const submitForm = async (data: z.infer<typeof newExportJobFormSchema>) => {
    try {
      if (!data.output_file_url) {
        toast.error('Output file URL is required.');
        return;
      }
      await createExportJob({
        workspace,
        data: {
          output_file_url: data.output_file_url,
          config: {
            limit: data.config?.limit,
            filters: data.config?.filters,
            search: data.config?.search,
            format_options: data.config?.format_options,
          },
        },
      });
      resetAndClose();
      toast.success('Export job created successfully!');
      queryClient.resetQueries({ queryKey: getListExportJobsQueryKey(workspace) });
    } catch (error) {
      websiteLogger.error(error instanceof Error ? error.message : 'Failed to create export job');
      toast.error('Failed to create export job. Please try again.');
    }
  };

  return (
    <>
      <Button color="brand" onClick={openModal}>
        Export Entries
      </Button>

      {isOpen && (
        <FormModal
          open
          className="w-auto min-w-[500px] max-w-[1300px]"
          title="Export Entries to Dataset"
          submitButtonText="Confirm"
          disabled={isCreatingExportJob}
          loading={isCreatingExportJob}
          onSubmit={form.handleSubmit(
            submitForm,
            handleFormErrorsGeneric({ title: 'New Export Job Form Errors' })
          )}
          onClose={resetAndClose}
        >
          <FormProvider {...form}>
            <NewExportJobForm />
          </FormProvider>
        </FormModal>
      )}
    </>
  );
};
