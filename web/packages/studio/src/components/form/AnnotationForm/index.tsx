// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { CodeEditor } from '@nemo/common/src/components/CodeEditor';
import { ContentType } from '@nemo/common/src/components/CodeEditor/constants';
import { ControlledTextInput } from '@nemo/common/src/components/form/ControlledTextInput';
import { buildAssistantResponse } from '@nemo/common/src/models/utils';
import { Stack, Flex, Label, FormField, Text, Block } from '@nvidia/foundations-react-core';
import { ThumbButton } from '@studio/components/buttons/ThumbButton';
import { ExpandableMessage } from '@studio/components/ExpandableMessage';
import { annotationFormFields } from '@studio/components/form/AnnotationForm/constants';
import { InfoTooltip } from '@studio/components/InfoTooltip';
import { ChatCompletion } from 'openai/resources/chat/completions';
import { ComponentProps, FC } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import { z } from 'zod';

interface Props {
  slotFooter?: React.ReactNode;
  attributes?: {
    Message?: ComponentProps<typeof ExpandableMessage>;
  };
}
export const AnnotationForm: FC<Props> = ({ attributes, slotFooter }) => {
  const form = useFormContext<z.infer<typeof annotationFormFields>>();
  const modelResponse = useWatch({ control: form.control, name: 'modelResponse' });
  const responseOverride = useWatch({ control: form.control, name: 'responseOverride' });
  const thumbValue = useWatch({ control: form.control, name: 'thumb' });
  const onThumbChange = (value: 'positive' | 'negative') => {
    if (thumbValue === value) {
      form.setValue('thumb', undefined);
      return;
    }
    form.setValue('thumb', value);
  };
  const codeEditorContent = responseOverride
    ? ((responseOverride.choices as ChatCompletion['choices'])[0].message.content ?? '')
    : (modelResponse ?? '');

  return (
    <Stack gap="8">
      <Stack gap="4">
        <Label>Model Response</Label>
        <Block className="bg-surface-overlay rounded-xl rounded-bl-none p-density-xl">
          <ExpandableMessage message={modelResponse} {...attributes?.Message} />
        </Block>
      </Stack>
      <Flex className="max-w-full" wrap="wrap" gap="6">
        <FormField
          // eslint-disable-next-line no-restricted-syntax
          style={{ containerType: 'normal' }}
          className="w-auto"
          aria-label="thumb"
          slotLabel="Thumb"
          slotError={form.formState.errors.thumb?.message}
          status={form.formState.errors.thumb ? 'error' : undefined}
        >
          <Flex className="inline-flex" gap="2">
            <ThumbButton
              direction="up"
              selected={thumbValue === 'positive'}
              onClick={() => onThumbChange('positive')}
            >
              Positive
            </ThumbButton>
            <ThumbButton
              direction="down"
              selected={thumbValue === 'negative'}
              onClick={() => onThumbChange('negative')}
            >
              Negative
            </ThumbButton>
          </Flex>
        </FormField>
        <ControlledTextInput
          formFieldProps={{
            className: 'w-auto',
            style: { containerType: 'normal' },
            slotInfo: 'Rating must be between 0.0 and 1.0',
          }}
          className="w-18"
          useControllerProps={{ name: 'rating' }}
          label="Rating"
          type="number"
          min={0}
          max={1}
          step={0.1}
        />
      </Flex>
      {/* Response Override */}
      <Stack gap="2">
        <Flex justify="between">
          <Label>
            <Text kind="label/bold/sm">Response Override</Text>
          </Label>
          <InfoTooltip message="An override replaces the model's original response with a new one. An override will always replace a rewrite." />
        </Flex>
        <FormField
          slotError={form.formState.errors.responseOverride?.message?.toString()}
          status={form.formState.errors.responseOverride ? 'error' : undefined}
        >
          <CodeEditor
            className="min-h-[200px] max-h-[400px] overflow-y-auto"
            contentType={ContentType.JSON}
            hideCopyButton
            content={codeEditorContent}
            onChange={(value) => {
              form.setValue('responseOverride', buildAssistantResponse(value));
            }}
          />
        </FormField>
      </Stack>
      {/* Disclaimer */}
      <Block className="bg-surface-overlay rounded-xl p-density-xl">
        <ExpandableMessage message="Changes will create a new annotation entry while preserving the original.  When exporting, only the most recent annotation will be used." />
      </Block>
      {slotFooter}
    </Stack>
  );
};
