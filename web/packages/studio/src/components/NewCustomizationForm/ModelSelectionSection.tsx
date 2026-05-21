// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ControlledTextInput } from '@nemo/common/src/components/form/ControlledTextInput';
import { ModelSelectV2, type ModelSelection } from '@nemo/common/src/components/ModelSelectV2';
import { groupModelsByWorkspace } from '@nemo/common/src/utils/models';
import { type ModelEntity } from '@nemo/sdk/generated/platform/schema';
import { Anchor, Block, Flex, FormField } from '@nvidia/foundations-react-core';
import { type CustomizationFormFields } from '@studio/components/NewCustomizationForm';
import { NEW_CUSTOMIZATION_FORM_HYP_DEFAULT_VALUES } from '@studio/components/NewCustomizationForm/constants';
import { FormSection } from '@studio/components/NewCustomizationForm/FormSection';
import { LINK_DOCS_FINE_TUNE_MODEL_ENTITIES } from '@studio/constants/links';
import { useMemo } from 'react';
import { useController, useFormContext } from 'react-hook-form';

interface ModelSelectionSectionProps {
  models?: ModelEntity[];
  isFetchingModels?: boolean;
}

export const ModelSelectionSection = ({ models, isFetchingModels }: ModelSelectionSectionProps) => {
  const {
    control,
    formState: { disabled },
    setValue,
  } = useFormContext<CustomizationFormFields>();

  const { field, fieldState } = useController({ control, name: 'model' });

  // TODO: Remove this once we have a way to search models by fileset not null
  const modelsWithFileset = useMemo(() => models?.filter((m) => m.fileset) ?? [], [models]);

  const groups = useMemo(
    () => groupModelsByWorkspace(modelsWithFileset, { sort: true }),
    [modelsWithFileset]
  );

  const value: ModelSelection | null = field.value ? { model: field.value as string } : null;

  const handleValueChange = (selection: ModelSelection) => {
    field.onChange(selection.model);
    setValue('training', NEW_CUSTOMIZATION_FORM_HYP_DEFAULT_VALUES, {
      shouldValidate: true,
    });
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) field.onBlur();
  };

  return (
    <FormSection
      title="Model Selection"
      description={
        <>
          Refer to the{' '}
          <Anchor href={LINK_DOCS_FINE_TUNE_MODEL_ENTITIES} target="_blank">
            Model Entities documentation
          </Anchor>{' '}
          for steps on customizing models.
        </>
      }
    >
      <Block data-testid="base-model-select">
        <FormField
          slotLabel="Base Model"
          status={fieldState.error ? 'error' : undefined}
          slotError={fieldState.error?.message}
        >
          <ModelSelectV2
            value={value}
            onValueChange={handleValueChange}
            groups={groups}
            loading={isFetchingModels}
            disabled={isFetchingModels || disabled}
            placeholder="Select a base model"
            hideAdapters
            fullWidth
            onOpenChange={handleOpenChange}
          />
        </FormField>
      </Block>
      <Flex gap="density-2xl" className="pt-density-xl">
        <ControlledTextInput
          label="Output Model Name"
          selectOnFocus
          useControllerProps={{ name: 'output.name', control }}
        />
        <ControlledTextInput
          label="Description (optional)"
          useControllerProps={{ name: 'description', control }}
        />
      </Flex>
    </FormSection>
  );
};
