// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { UseControllerComponentProps } from '@nemo/common/src/types';
import { FormField, TextArea } from '@nvidia/foundations-react-core';
import { ComponentProps } from 'react';
import { useController } from 'react-hook-form';

interface Props extends ComponentProps<typeof TextArea>, UseControllerComponentProps {
  label?: string;
}

export const ControlledTextArea = ({
  useControllerProps,
  label,
  formFieldProps,
  attributes,
  ...props
}: Props) => {
  const {
    field: { onChange, value, disabled },
    fieldState: { error },
  } = useController(useControllerProps);
  const wrappedOnChange: NonNullable<ComponentProps<typeof TextArea>['onChange']> = (e) => {
    props?.onChange?.(e);
    onChange(e);
  };
  return (
    <FormField
      slotLabel={label}
      slotError={error?.message || ''}
      aria-label={label}
      status={error ? 'error' : undefined}
      {...formFieldProps}
    >
      <TextArea
        attributes={attributes}
        {...props}
        value={value}
        onChange={wrappedOnChange}
        disabled={props.disabled || disabled}
        status={error ? 'error' : undefined}
      />
    </FormField>
  );
};
