// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { UseControllerComponentProps } from '@nemo/common/src/types';
import { DatePicker, FormField } from '@nvidia/foundations-react-core';
import { ComponentProps } from 'react';
import { useController } from 'react-hook-form';

// Generic type to handle both single and range selection
type DatePickerValue<T extends 'single' | 'range'> = T extends 'single'
  ? Date | undefined
  : { from?: Date; to?: Date };

interface RangeKeys {
  from: string;
  to: string;
}

const DEFAULT_RANGE_KEYS: RangeKeys = { from: 'from', to: 'to' };

interface Props<T extends 'single' | 'range' = 'single'>
  extends
    Omit<
      ComponentProps<typeof DatePicker>,
      'onChange' | 'defaultValue' | 'value' | 'kind' | 'onValueChange' | 'placeholder'
    >,
    UseControllerComponentProps {
  hideError?: boolean;
  onChange?: (value: DatePickerValue<T>) => void;
  kind?: T;
  placeholder?: T extends 'single' ? string : string | { from?: string; to?: string };
  /**
   * Custom keys for storing range values in the form.
   * Only applicable when kind="range".
   * @default { from: 'from', to: 'to' }
   * @example { from: 'start', to: 'end' }
   */
  rangeKeys?: RangeKeys;
}

export const ControlledDatePicker = <T extends 'single' | 'range' = 'single'>({
  kind = 'single' as T,
  hideError,
  onChange,
  formFieldProps,
  useControllerProps,
  placeholder = 'yyyy-mm-dd',
  rangeKeys = DEFAULT_RANGE_KEYS,
  ...datePickerProps
}: Props<T>) => {
  const {
    field: { onBlur, onChange: onChangeControl, value },
    fieldState: { error },
  } = useController(useControllerProps);

  const handleValueChangeSingle = (newValue?: Date) => {
    onChange?.(newValue as DatePickerValue<T>);
    onChangeControl(newValue);
  };

  const handleValueChangeRange = (newValue?: { from?: Date; to?: Date }) => {
    // Transform from DatePicker's from/to to custom keys
    const transformedValue = newValue
      ? { [rangeKeys.from]: newValue.from, [rangeKeys.to]: newValue.to }
      : undefined;

    onChange?.(newValue as DatePickerValue<T>);
    onChangeControl(transformedValue);
  };

  // Transform form value (custom keys) to DatePicker value (from/to)
  const getDatePickerRangeValue = () => {
    if (!value) return undefined;
    return {
      from: value[rangeKeys.from],
      to: value[rangeKeys.to],
    };
  };

  return (
    <FormField
      name={useControllerProps.name}
      slotError={hideError ? undefined : error?.message}
      status={error && 'error'}
      {...formFieldProps}
    >
      {() => {
        if (kind === 'range') {
          return (
            <DatePicker
              kind="range"
              value={getDatePickerRangeValue()}
              onBlur={onBlur}
              onValueChange={handleValueChangeRange}
              placeholder={placeholder as string | { from?: string; to?: string }}
              format="yyyy-MM-dd"
              {...datePickerProps}
            />
          );
        }

        return (
          <DatePicker
            kind="single"
            value={value}
            onBlur={onBlur}
            onValueChange={handleValueChangeSingle}
            placeholder={placeholder as string}
            format="yyyy-MM-dd"
            {...datePickerProps}
          />
        );
      }}
    </FormField>
  );
};
