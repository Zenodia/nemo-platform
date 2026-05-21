// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ChatCompletionInput } from '@nemo/common/src/components/ChatCompletionInput';
import { SegmentedControl, Stack, Text } from '@nvidia/foundations-react-core';
import { MetricTestPanel } from '@studio/components/evaluation/Jobs/form/MetricTestPanel';
import { JudgeModelSelect } from '@studio/components/evaluation/JudgeModelSelect';
import { mergeInferenceParamsFormValues } from '@studio/hooks/evaluation/useCreateConfigurationForm';
import { type MetricPanelFormData } from '@studio/hooks/evaluation/useMetricPanelForm';
import { type FC, useState } from 'react';
import { useFieldArray, useFormContext } from 'react-hook-form';

type ActivePanel = 'configure' | 'test';

const SEGMENTED_CONTROL_ITEMS = [
  { value: 'configure', children: 'Configure' },
  { value: 'test', children: 'Test' },
];

interface MetricRightPanelProps {
  onSuccessfulTestRun: () => void;
}

export const MetricLLMJudgePanel: FC<MetricRightPanelProps> = ({ onSuccessfulTestRun }) => {
  const { control, watch, setValue } = useFormContext<MetricPanelFormData>();
  const [activePanel, setActivePanel] = useState<ActivePanel>('configure');
  const { fields, append, remove, move } = useFieldArray({ control, name: 'body.messages' });
  const inferenceParams = watch('body.inference');

  return (
    <>
      <SegmentedControl
        value={activePanel}
        onValueChange={(v) => setActivePanel(v as ActivePanel)}
        items={SEGMENTED_CONTROL_ITEMS}
        className="w-full shrink-0"
      />

      {/*
        Keep both panels mounted so MetricTestPanel local state (sample data, file selection,
        results) survives switching Configure ↔ Test. Use `hidden` instead of conditional render.
      */}
      <Stack
        gap="6"
        className={
          activePanel === 'configure' ? 'min-h-0 flex-1 overflow-y-auto' : 'hidden min-h-0 flex-1'
        }
      >
        <Stack gap="1">
          <Text kind="body/bold/lg">Model &amp; Prompt</Text>
          <Text kind="body/regular/md" className="text-secondary">
            Provide instructions for the judge, with variables that get filled from your dataset.
            Customize the judge prompt to match your evaluation criteria.
          </Text>
        </Stack>

        <Stack gap="2">
          <JudgeModelSelect<MetricPanelFormData>
            formFieldName="body.model.name"
            required
            showParams
            inferenceParams={inferenceParams}
            onInferenceParamsChange={(params) =>
              setValue('body.inference', mergeInferenceParamsFormValues(inferenceParams, params))
            }
          />

          <Stack gap="2">
            {fields.map((field, index) => (
              <ChatCompletionInput<MetricPanelFormData>
                key={field.id}
                control={control}
                name={`body.messages.${index}`}
                fieldArrayLength={fields.length}
                onMoveUp={index > 0 ? () => move(index, index - 1) : undefined}
                onMoveDown={index < fields.length - 1 ? () => move(index, index + 1) : undefined}
                onDuplicate={() =>
                  append(
                    { role: field.role, content: field.content, expanded: true },
                    { shouldFocus: false }
                  )
                }
                onRemove={() => remove(index)}
                allowRemove={fields.length > 1}
              />
            ))}
          </Stack>
        </Stack>
      </Stack>

      <div
        className={
          activePanel === 'test' ? 'flex min-h-0 min-w-0 flex-1 flex-col' : 'hidden min-h-0 flex-1'
        }
      >
        <MetricTestPanel onSuccessfulTestRun={onSuccessfulTestRun} />
      </div>
    </>
  );
};
