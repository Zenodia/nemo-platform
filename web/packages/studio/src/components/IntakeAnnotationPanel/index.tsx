// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { zodResolver } from '@hookform/resolvers/zod';
import { LoadingButton } from '@nemo/common/src/components/LoadingButton';
import { useToast } from '@nemo/common/src/providers/toast/useToast';
import { Entry } from '@nemo/sdk/generated/platform/schema';
import { Flex, Panel, Stack } from '@nvidia/foundations-react-core';
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
  entry: Entry;
  attributes?: {
    Panel?: ComponentProps<typeof Panel>;
  };
}

export const IntakeAnnotationPanel: FC<Props> = ({ entry, attributes }) => {
  const toast = useToast();
  const workspace = useWorkspaceFromPath();
  const form = useForm<z.infer<typeof annotationFormFields>>({
    resolver: zodResolver(annotationFormFields),
    mode: 'onChange',
    values: {
      modelResponse: getEntryResponseContent(entry),
    },
  });

  const { mutateAsync: createAnnotation, isPending: isCreatingAnnotation } =
    useCreateReviewerAnnotation({ workspace, entryId: entry.id });
  const onSubmit = async (data: z.infer<typeof annotationFormFields>) => {
    if (!entry.id) {
      toast.error('Cannot create annotation without an existing entry.');
      return;
    }
    await createAnnotation({
      workspace,
      name: entry.id,
      data: { events: [formToReviewerAnnotationEvent(data)] },
    });
  };

  const errorMessage = form.formState.errors.hasChanges?.message ? (
    <AnnotationErrorMessage message={form.formState.errors.hasChanges.message} />
  ) : undefined;
  const flexJustify = errorMessage ? 'between' : 'end';

  return (
    <Panel elevation="high" {...attributes?.Panel}>
      <Stack justify="between" gap="6">
        <FormProvider {...form}>
          <form
            onSubmit={form.handleSubmit(
              onSubmit,
              handleFormErrorsGeneric({ title: 'Annotation Form Errors' })
            )}
          >
            <AnnotationForm
              slotFooter={
                <Flex justify={flexJustify}>
                  {errorMessage}
                  <LoadingButton
                    className="self-end"
                    kind="primary"
                    color="brand"
                    type="submit"
                    disabled={isCreatingAnnotation}
                    loading={isCreatingAnnotation}
                  >
                    Submit
                  </LoadingButton>
                </Flex>
              }
            />
          </form>
        </FormProvider>
      </Stack>
    </Panel>
  );
};
