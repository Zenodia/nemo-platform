// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { zodResolver } from '@hookform/resolvers/zod';
import { FormModal } from '@nemo/common/src/components/FormModal';
import { useToast } from '@nemo/common/src/providers/toast/useToast';
import { Entry } from '@nemo/sdk/generated/platform/schema';
import { ExpandableMessage } from '@studio/components/ExpandableMessage';
import { AnnotationForm } from '@studio/components/form/AnnotationForm';
import { AnnotationErrorMessage } from '@studio/components/form/AnnotationForm/AnnotationErrorMessage';
import { annotationFormFields } from '@studio/components/form/AnnotationForm/constants';
import { useCreateReviewerAnnotation } from '@studio/components/form/AnnotationForm/useCreateReviewerAnnotation';
import { formToReviewerAnnotationEvent } from '@studio/components/form/AnnotationForm/utils';
import { getEntryResponseContent } from '@studio/components/IntakeEntriesTable/utils';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { handleFormErrorsGeneric } from '@studio/util/forms/error';
import { ComponentProps, FC } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { z } from 'zod';

interface Props {
  entry?: Entry;
  open: boolean;
  onClose: () => void;
  attributes?: {
    FormModal?: ComponentProps<typeof FormModal>;
    Message?: ComponentProps<typeof ExpandableMessage>;
  };
}
export const AnnotationModal: FC<Props> = ({ open, onClose, entry, attributes }) => {
  const toast = useToast();
  const workspace = useWorkspaceFromPath();
  const { mutateAsync: addEvents, isPending: isAddingEvents } = useCreateReviewerAnnotation({
    workspace,
  });
  const form = useForm({
    resolver: zodResolver(annotationFormFields),
    mode: 'onChange',
    values: {
      modelResponse: getEntryResponseContent(entry),
    },
  });

  const resetAndClose = () => {
    form.reset();
    onClose();
  };

  const onSubmit = async (data: z.infer<typeof annotationFormFields>) => {
    if (!entry || !entry.id) {
      toast.error('Cannot create annotation without an existing entry.');
      return;
    }

    await addEvents({
      workspace,
      name: entry.id,
      data: { events: [formToReviewerAnnotationEvent(data)] },
    });
    resetAndClose();
  };

  const errorText = form.formState.errors.hasChanges?.message ? (
    <AnnotationErrorMessage message={form.formState.errors.hasChanges.message} />
  ) : undefined;

  return (
    <FormModal
      className="w-[700px]"
      open={open}
      onClose={resetAndClose}
      title="Annotation"
      submitButtonText="Save"
      cancelButtonText="Cancel"
      onSubmit={form.handleSubmit(
        onSubmit,
        handleFormErrorsGeneric({ title: 'Annotation Modal Errors' })
      )}
      loading={isAddingEvents}
      slotFooterLeft={errorText}
      {...attributes?.FormModal}
    >
      <FormProvider {...form}>
        <AnnotationForm attributes={attributes} />
      </FormProvider>
    </FormModal>
  );
};
