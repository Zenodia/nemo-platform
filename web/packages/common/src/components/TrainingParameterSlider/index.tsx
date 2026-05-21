// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { SliderWithTextInput } from '@nemo/common/src/components/SliderWithTextInput';
import {
  CustomizerHyperparameters,
  HYPERPARAMETER_FIELD_METADATA,
  validateTrainingParameterIsInRange,
} from '@nemo/common/src/components/TrainingParameterSlider/types';
import { FC } from 'react';
import { Controller, FieldPath, useFormContext } from 'react-hook-form';

export interface TrainingParameterSliderProps {
  name: FieldPath<CustomizerHyperparameters>;
  disabled?: boolean;
  errorText?: string;
}

export const TrainingParameterSlider: FC<TrainingParameterSliderProps> = ({
  name,
  disabled,
  errorText: errorTextOverride,
}) => {
  const { control } = useFormContext<CustomizerHyperparameters>();

  const fieldMetadata = HYPERPARAMETER_FIELD_METADATA[name];

  return (
    <Controller
      control={control}
      name={name}
      rules={{
        validate: {
          isInRange: (value) =>
            validateTrainingParameterIsInRange(value, fieldMetadata.min, fieldMetadata.max),
        },
      }}
      render={({ field, fieldState }) => (
        <SliderWithTextInput
          id={`${name}-slider`}
          field={field}
          defaultValue={fieldMetadata.default}
          min={fieldMetadata.min ?? 0}
          max={fieldMetadata.max ?? 0}
          step={fieldMetadata.step ?? 1}
          disabled={disabled}
          formFieldProps={{
            slotLabel: fieldMetadata.name,
            slotHelp: fieldMetadata.description,
            slotError: fieldState.error?.message || errorTextOverride,
          }}
          attributes={{
            Slider: {
              customSteps: fieldMetadata.customSteps ?? [fieldMetadata.min, fieldMetadata.max],
              stepFormatFn(value) {
                if (value === 1e-15) {
                  return '1e-15';
                }
                return value.toString();
              },
            },
          }}
        />
      )}
    />
  );
};
