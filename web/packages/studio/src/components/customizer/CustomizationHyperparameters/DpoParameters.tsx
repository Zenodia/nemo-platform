// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ZodFormField } from '@nemo/common/src/components/form/ZodFormField';
import { dpoSchema } from '@nemo/common/src/components/TrainingParameterSlider/types';
import {
  AccordionContent,
  AccordionItem,
  AccordionRoot,
  AccordionTrigger,
  Stack,
  Text,
} from '@nvidia/foundations-react-core';
import { CustomizationFormFields } from '@studio/components/NewCustomizationForm';
import { FormSection } from '@studio/components/NewCustomizationForm/FormSection';
import { useFormContext } from 'react-hook-form';

export const DpoParameters = () => {
  const { control } = useFormContext<CustomizationFormFields>();
  return (
    <FormSection title="DPO Parameters">
      <ZodFormField
        schema={dpoSchema.shape.max_grad_norm}
        min={0}
        max={10}
        step={0.1}
        useControllerProps={{ name: 'training.max_grad_norm', control }}
      />

      <AccordionRoot multiple>
        <AccordionItem value="advanced-dpo" className="border-b-0">
          <AccordionTrigger>
            <Text kind="label/bold/md">Show Advanced DPO Parameters</Text>
          </AccordionTrigger>
          <AccordionContent>
            <Stack gap="density-lg" className="pt-density-md">
              <ZodFormField
                schema={dpoSchema.shape.ref_policy_kl_penalty}
                min={0}
                max={10}
                step={0.01}
                formFieldProps={{
                  slotLabel: 'Ref Policy KL Penalty',
                }}
                useControllerProps={{ name: 'training.ref_policy_kl_penalty', control }}
              />
              <ZodFormField
                schema={dpoSchema.shape.preference_loss_weight}
                min={0}
                max={10}
                step={0.1}
                useControllerProps={{ name: 'training.preference_loss_weight', control }}
              />
              <ZodFormField
                schema={dpoSchema.shape.preference_average_log_probs}
                formFieldProps={{
                  labelPosition: 'left',
                }}
                useControllerProps={{
                  name: 'training.preference_average_log_probs',
                  control,
                }}
              />
              <ZodFormField
                schema={dpoSchema.shape.sft_loss_weight}
                min={0}
                max={10}
                step={0.1}
                formFieldProps={{
                  slotLabel: 'SFT Loss Weight',
                }}
                useControllerProps={{ name: 'training.sft_loss_weight', control }}
              />
              <ZodFormField
                schema={dpoSchema.shape.sft_average_log_probs}
                formFieldProps={{
                  slotLabel: 'SFT Average Log Probs',
                  labelPosition: 'left',
                }}
                useControllerProps={{ name: 'training.sft_average_log_probs', control }}
              />
            </Stack>
          </AccordionContent>
        </AccordionItem>
      </AccordionRoot>
    </FormSection>
  );
};
