// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { TextInput, type TextInputProps } from '@nvidia/foundations-react-core';
import { useEffect, useState, type JSX } from 'react';

export interface DebouncedTextInputProps extends TextInputProps {
  /**
   * The number of milliseconds to debounce the onValueChange handler.
   * @defaultValue 500
   */
  debounce?: number;
}

/** A TextInput component with a debounced onValueChange handler. */
export function DebouncedTextInput({
  debounce = 500,
  onValueChange,
  value: initialValue = '',
  ...props
}: DebouncedTextInputProps): JSX.Element {
  const [value, setValue] = useState(initialValue ?? '');

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      onValueChange?.(value);
    }, debounce);
    return () => clearTimeout(timeout);
  }, [debounce, onValueChange, value]);

  return <TextInput {...props} value={value} onValueChange={setValue} />;
}
