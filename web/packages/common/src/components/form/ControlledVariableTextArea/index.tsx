// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  VariableTextArea,
  type VariableTextAreaHandle,
  type VariableTextAreaProps,
} from '@nemo/common/src/components/form/VariableTextArea';
import type { UseControllerComponentProps } from '@nemo/common/src/types';
import { FormField } from '@nvidia/foundations-react-core';
import { forwardRef } from 'react';
import { useController } from 'react-hook-form';

export interface ControlledVariableTextAreaProps
  extends Omit<VariableTextAreaProps, 'value' | 'onChange'>, UseControllerComponentProps {}

export const ControlledVariableTextArea = forwardRef<
  VariableTextAreaHandle,
  ControlledVariableTextAreaProps
>(({ useControllerProps, formFieldProps, ...props }, ref) => {
  const {
    field: { onChange, value, disabled },
    fieldState: { error },
  } = useController(useControllerProps);
  return (
    <FormField
      slotError={error?.message || ''}
      status={error ? 'error' : undefined}
      {...formFieldProps}
    >
      <VariableTextArea
        ref={ref}
        {...props}
        value={typeof value === 'string' ? value : ''}
        onChange={onChange}
        disabled={props.disabled || disabled}
      />
    </FormField>
  );
});

ControlledVariableTextArea.displayName = 'ControlledVariableTextArea';
