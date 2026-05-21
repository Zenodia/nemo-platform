// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { UseControllerComponentProps } from '@nemo/common/src/types';
import { SegmentedControl } from '@nvidia/foundations-react-core';
import type { ComponentProps, FC } from 'react';
import { useController } from 'react-hook-form';

interface Props extends ComponentProps<typeof SegmentedControl>, UseControllerComponentProps {}

export const ControlledSegmentedControl: FC<Props> = ({
  useControllerProps,
  // eslint-disable-next-line unused-imports/no-unused-vars
  formFieldProps: _formFieldProps,
  ...props
}) => {
  const { field } = useController(useControllerProps);

  return (
    <SegmentedControl {...props} value={field.value} onValueChange={(v) => field.onChange(v)} />
  );
};
