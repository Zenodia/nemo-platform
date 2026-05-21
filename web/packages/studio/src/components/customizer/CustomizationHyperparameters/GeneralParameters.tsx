// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ZodFormField } from '@nemo/common/src/components/form/ZodFormField';
import {
  hyperparametersSchema,
  MODEL_CONFIGS_WITH_SEQUENCE_PACKING,
} from '@nemo/common/src/components/TrainingParameterSlider/types';
import {
  AccordionContent,
  AccordionItem,
  AccordionRoot,
  AccordionTrigger,
  Anchor,
  Stack,
  Text,
} from '@nvidia/foundations-react-core';
import type { CustomizationFormFields } from '@studio/components/NewCustomizationForm';
import { FormSection } from '@studio/components/NewCustomizationForm/FormSection';
import {
  LINK_DOCS_FINE_TUNE_HYPERPARAMETERS,
  LINK_DOCS_SEQUENCE_PACKING,
} from '@studio/constants/links';
import type { FC } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';

export const GeneralParameters: FC = () => {
  const { control } = useFormContext<CustomizationFormFields>();
  const selectedModel = useWatch({ control, name: 'model' });
  const isSequencePackingEnabled = MODEL_CONFIGS_WITH_SEQUENCE_PACKING.some((model) =>
    typeof selectedModel === 'string' ? selectedModel.includes(model) : false
  );

  return (
    <FormSection
      title="Training Parameters"
      description={
        <>
          Configure how your model is trained. To learn more, refer to{' '}
          <Anchor href={LINK_DOCS_FINE_TUNE_HYPERPARAMETERS} target="_blank">
            Hyperparameters
          </Anchor>
          .
        </>
      }
    >
      <Stack gap="density-lg" className="pt-density-md">
        <ZodFormField
          schema={hyperparametersSchema.shape.epochs}
          min={1}
          max={100}
          step={1}
          useControllerProps={{ name: 'training.epochs', control }}
          formFieldProps={{ labelPosition: 'left' }}
        />
        <ZodFormField
          schema={hyperparametersSchema.shape.learning_rate}
          min={1e-6}
          max={1e-3}
          step={1e-6}
          useControllerProps={{ name: 'training.learning_rate', control }}
        />
        <ZodFormField
          schema={hyperparametersSchema.shape.batch_size}
          min={1}
          max={256}
          step={1}
          useControllerProps={{ name: 'training.batch_size', control }}
        />
        <ZodFormField
          schema={hyperparametersSchema.shape.max_seq_length}
          min={1}
          max={131072}
          step={1}
          useControllerProps={{ name: 'training.max_seq_length', control }}
        />
        <ZodFormField
          disabled={!isSequencePackingEnabled}
          schema={hyperparametersSchema.shape.sequence_packing}
          formFieldProps={{
            labelPosition: 'left',
            slotInfo: !isSequencePackingEnabled ? (
              <span>
                Sequence packing is not supported for this model. See{' '}
                <Anchor href={LINK_DOCS_SEQUENCE_PACKING} target="_blank" rel="noopener noreferrer">
                  the docs
                </Anchor>{' '}
                for more details.
              </span>
            ) : (
              hyperparametersSchema.shape.sequence_packing.description
            ),
          }}
          useControllerProps={{ name: 'training.sequence_packing', control }}
        />
      </Stack>

      <AccordionRoot multiple>
        <AccordionItem value="advanced" className="border-b-0">
          <AccordionTrigger>
            <Text kind="label/bold/md">Show Advanced Training Parameters</Text>
          </AccordionTrigger>
          <AccordionContent>
            <Stack gap="density-lg" className="pt-density-md">
              <ZodFormField
                schema={hyperparametersSchema.shape.micro_batch_size}
                min={1}
                max={64}
                step={1}
                useControllerProps={{ name: 'training.micro_batch_size', control }}
              />
              <ZodFormField
                schema={hyperparametersSchema.shape.warmup_steps}
                min={0}
                max={1000}
                step={1}
                useControllerProps={{ name: 'training.warmup_steps', control }}
              />
              <ZodFormField
                schema={hyperparametersSchema.shape.weight_decay}
                min={0}
                max={1}
                step={0.01}
                useControllerProps={{ name: 'training.weight_decay', control }}
              />
              <ZodFormField
                schema={hyperparametersSchema.shape.min_learning_rate}
                min={0}
                max={1e-3}
                step={1e-6}
                useControllerProps={{ name: 'training.min_learning_rate', control }}
                formFieldProps={{ labelPosition: 'left' }}
              />
              <ZodFormField
                schema={hyperparametersSchema.shape.precision}
                useControllerProps={{ name: 'training.precision', control }}
                formFieldProps={{ labelPosition: 'left' }}
              />
              <ZodFormField
                schema={hyperparametersSchema.shape.optimizer}
                useControllerProps={{ name: 'training.optimizer', control }}
                formFieldProps={{ labelPosition: 'left' }}
              />

              <ZodFormField
                schema={hyperparametersSchema.shape.seed}
                min={0}
                max={2147483647}
                step={1}
                useControllerProps={{ name: 'training.seed', control }}
                formFieldProps={{ labelPosition: 'left' }}
              />
              <ZodFormField
                schema={hyperparametersSchema.shape.log_every_n_steps}
                min={0}
                max={1000}
                step={1}
                useControllerProps={{ name: 'training.log_every_n_steps', control }}
              />
              <ZodFormField
                schema={hyperparametersSchema.shape.val_check_interval}
                min={0}
                max={1000}
                step={0.01}
                useControllerProps={{ name: 'training.val_check_interval', control }}
              />
              <ZodFormField
                schema={hyperparametersSchema.shape.max_steps}
                min={-1}
                max={1000}
                step={1}
                useControllerProps={{ name: 'training.max_steps', control }}
              />
            </Stack>
          </AccordionContent>
        </AccordionItem>
      </AccordionRoot>
    </FormSection>
  );
};
