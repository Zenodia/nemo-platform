// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { SliderWithTextInput } from '@nemo/common/src/components/SliderWithTextInput';
import {
  type ModelInferenceParameters,
  MODEL_HYPERPARAMETER_FIELD_METADATA,
} from '@nemo/common/src/constants/inferenceParameters';
import { FC } from 'react';
import { Controller, FieldPath, useFormContext } from 'react-hook-form';

export interface ModelParameterSliderProps {
  name: FieldPath<ModelInferenceParameters>;
}

export const ModelParameterSlider: FC<ModelParameterSliderProps> = ({ name }) => {
  const {
    control,
    formState: { disabled, errors },
  } = useFormContext<ModelInferenceParameters>();

  const fieldMetadata = MODEL_HYPERPARAMETER_FIELD_METADATA[name];
  return (
    <Controller
      control={control}
      name={name}
      render={({ field }) => (
        <SliderWithTextInput
          id={`${name}-slider`}
          field={field}
          defaultValue={fieldMetadata.default}
          disabled={disabled}
          min={fieldMetadata.min}
          max={fieldMetadata.max}
          step={fieldMetadata.step ?? 1}
          size="compact"
          formFieldProps={{
            slotLabel: fieldMetadata.name,
            slotError: disabled ? undefined : errors[name]?.message,
            slotInfo: fieldMetadata.description,
          }}
          showStepMarkers
          attributes={{
            Slider: {
              stepFormatFn(value) {
                return value.toString();
              },
            },
          }}
        />
      )}
    />
  );
};
