// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ControlledCombobox } from '@nemo/common/src/components/form/ControlledCombobox';
import { ZodFormField } from '@nemo/common/src/components/form/ZodFormField';
import { loraSchema } from '@nemo/common/src/components/TrainingParameterSlider/types';
import {
  AccordionContent,
  AccordionItem,
  AccordionRoot,
  AccordionTrigger,
  Flex,
  FormField,
  Select,
  Stack,
  Switch,
  Text,
  Tooltip,
} from '@nvidia/foundations-react-core';
import { CustomizationFormFields } from '@studio/components/NewCustomizationForm';
import { Info } from 'lucide-react';
import { useFormContext, useWatch } from 'react-hook-form';

const RANK_OPTIONS = [1, 2, 4, 8, 16, 32, 64, 128, 256].map((v) => ({
  value: String(v),
  children: String(v),
}));

const quantizationSchema = loraSchema.shape.quantization.unwrap();

export const LoraParameters = () => {
  const {
    control,
    setValue,
    formState: { disabled },
  } = useFormContext<CustomizationFormFields>();

  const rank = useWatch({ control, name: 'training.peft.rank' });
  const quantization = useWatch({ control, name: 'training.peft.quantization' });
  const isQLoraEnabled = !!quantization;

  const handleQLoraToggle = (checked: boolean) => {
    if (checked) {
      setValue('training.peft.quantization', { precision: '4bit' }, { shouldValidate: true });
    } else {
      setValue('training.peft.quantization', undefined, { shouldValidate: true });
    }
  };

  return (
    <Stack gap="density-lg" className="pt-density-md">
      <FormField
        labelPosition="left"
        slotLabel={
          <Flex align="center" gap="density-xs">
            <Text kind="label/regular/md">Rank</Text>
            {loraSchema.shape.rank.description && (
              <Tooltip slotContent={loraSchema.shape.rank.description} side="top">
                <Info className="shrink-0" />
              </Tooltip>
            )}
          </Flex>
        }
      >
        <Select
          data-testid="lora-rank"
          placeholder="Select rank"
          value={String(rank ?? loraSchema.shape.rank._def.defaultValue())}
          onValueChange={(value: string | string[]) => {
            if (typeof value === 'string') {
              setValue('training.peft.rank', Number(value), { shouldValidate: true });
            }
          }}
          items={RANK_OPTIONS}
          disabled={disabled}
        />
      </FormField>
      <Flex align="center" justify="between">
        <Text kind="body/regular/md">Enable QLoRA</Text>
        <Switch checked={isQLoraEnabled} onCheckedChange={handleQLoraToggle} disabled={disabled} />
      </Flex>
      {isQLoraEnabled && (
        <ZodFormField
          schema={quantizationSchema.shape.precision}
          formFieldProps={{
            slotLabel: 'QLoRA Precision',
            labelPosition: 'left',
          }}
          useControllerProps={{ name: 'training.peft.quantization.precision', control }}
        />
      )}

      <AccordionRoot multiple>
        <AccordionItem value="advanced-lora" className="border-b-0">
          <AccordionTrigger>
            <Text kind="label/bold/md">Show Advanced LoRA Parameters</Text>
          </AccordionTrigger>
          <AccordionContent>
            <Stack gap="density-lg" className="pt-density-md">
              <ZodFormField
                schema={loraSchema.shape.alpha}
                min={1}
                max={Number.MAX_SAFE_INTEGER}
                step={1}
                useControllerProps={{ name: 'training.peft.alpha', control }}
                formFieldProps={{ labelPosition: 'left' }}
              />
              <ZodFormField
                schema={loraSchema.shape.dropout}
                min={0}
                max={1}
                step={0.01}
                useControllerProps={{ name: 'training.peft.dropout', control }}
              />
              <ControlledCombobox
                kind="multiple"
                items={['linear_qkv', 'linear_proj', 'linear_fc1', 'linear_fc2', '*_proj']}
                placeholder="Select target modules..."
                formFieldProps={{
                  slotLabel: <Text kind="label/regular/md">Target Modules</Text>,
                  labelPosition: 'left',
                  slotInfo: loraSchema.shape.target_modules.description,
                }}
                useControllerProps={{ name: 'training.peft.target_modules', control }}
              />
            </Stack>
          </AccordionContent>
        </AccordionItem>
      </AccordionRoot>
    </Stack>
  );
};
