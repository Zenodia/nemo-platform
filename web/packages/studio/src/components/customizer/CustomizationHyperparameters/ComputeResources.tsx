// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ZodFormField } from '@nemo/common/src/components/form/ZodFormField';
import { hyperparametersSchema } from '@nemo/common/src/components/TrainingParameterSlider/types';
import {
  AccordionContent,
  AccordionItem,
  AccordionRoot,
  AccordionTrigger,
  Stack,
  Text,
} from '@nvidia/foundations-react-core';
import type { CustomizationFormFields } from '@studio/components/NewCustomizationForm';
import { FormSection } from '@studio/components/NewCustomizationForm/FormSection';
import type { FC } from 'react';
import { useFormContext } from 'react-hook-form';

const parallelismSchema = hyperparametersSchema.shape.parallelism.unwrap();

export const ComputeResources: FC = () => {
  const { control } = useFormContext<CustomizationFormFields>();

  return (
    <FormSection
      title="Compute Resources"
      description="Configure GPU allocation for your training job."
    >
      <Stack gap="density-lg" className="pt-density-md">
        <ZodFormField
          schema={parallelismSchema.shape.num_nodes}
          min={1}
          max={16}
          step={1}
          useControllerProps={{ name: 'training.parallelism.num_nodes', control }}
        />
        <ZodFormField
          schema={parallelismSchema.shape.num_gpus_per_node}
          min={1}
          max={8}
          step={1}
          useControllerProps={{ name: 'training.parallelism.num_gpus_per_node', control }}
        />
      </Stack>

      <AccordionRoot multiple>
        <AccordionItem value="advanced-parallelism" className="border-b-0">
          <AccordionTrigger>
            <Text kind="label/bold/md">Show Advanced Parallelism</Text>
          </AccordionTrigger>
          <AccordionContent>
            <Stack gap="density-lg" className="pt-density-md">
              <ZodFormField
                schema={parallelismSchema.shape.tensor_parallel_size}
                min={1}
                max={8}
                step={1}
                useControllerProps={{
                  name: 'training.parallelism.tensor_parallel_size',
                  control,
                }}
              />
              <ZodFormField
                schema={parallelismSchema.shape.pipeline_parallel_size}
                min={1}
                max={8}
                step={1}
                useControllerProps={{
                  name: 'training.parallelism.pipeline_parallel_size',
                  control,
                }}
              />
              <ZodFormField
                schema={parallelismSchema.shape.context_parallel_size}
                min={1}
                max={8}
                step={1}
                useControllerProps={{
                  name: 'training.parallelism.context_parallel_size',
                  control,
                }}
              />
              <ZodFormField
                schema={parallelismSchema.shape.expert_parallel_size}
                min={1}
                max={8}
                step={1}
                useControllerProps={{
                  name: 'training.parallelism.expert_parallel_size',
                  control,
                }}
              />
              <ZodFormField
                schema={parallelismSchema.shape.sequence_parallel}
                formFieldProps={{ labelPosition: 'left' }}
                useControllerProps={{
                  name: 'training.parallelism.sequence_parallel',
                  control,
                }}
              />
            </Stack>
          </AccordionContent>
        </AccordionItem>
      </AccordionRoot>
    </FormSection>
  );
};
