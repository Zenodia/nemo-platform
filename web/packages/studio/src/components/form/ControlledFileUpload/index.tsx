// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { UseControllerComponentProps } from '@nemo/common/src/types';
import { DatasetFileUpload } from '@studio/components/DatasetFileUpload';
import { ComponentProps } from 'react';
import { useController, useWatch } from 'react-hook-form';

interface Props extends ComponentProps<typeof DatasetFileUpload>, UseControllerComponentProps {}

export const ControlledFileUpload = ({ useControllerProps, ...props }: Props) => {
  const {
    field: { onChange, disabled },
    fieldState: { error },
  } = useController(useControllerProps);
  const file = useWatch({ control: useControllerProps.control, name: useControllerProps.name });
  const wrappedOnChange = (files?: File | File[]) => {
    props?.onChange?.(files);
    onChange(files);
  };

  return (
    <DatasetFileUpload
      {...props}
      files={file ? [file] : undefined}
      onChange={wrappedOnChange}
      errorText={props.errorText || error?.message?.toString()}
      disabled={props.disabled || disabled}
    />
  );
};
