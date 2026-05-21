// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { TextInputSpinner } from '@nemo/common/src/components/form/TextInputSpinner';
import { UseControllerComponentProps } from '@nemo/common/src/types';
import { Combobox, ComboboxProps, FormField } from '@nvidia/foundations-react-core';
import { ReactNode, useState } from 'react';
import { useController } from 'react-hook-form';

// Generic type to handle both single and multiple selection
type ComboboxValue<T extends 'single' | 'multiple'> = T extends 'single' ? string : string[];
type ComboboxRenderSelectedValue<T extends 'single' | 'multiple'> = T extends 'single'
  ? (args: { selectedValue: string; setSelectedValue: (value: string) => void }) => ReactNode
  : (args: { selectedValue: string[]; setSelectedValue: (value: string[]) => void }) => ReactNode;

interface Props<T extends 'single' | 'multiple' = 'single'>
  // Omit ensures type safety and avoids uncontrolled component state
  extends
    Omit<
      ComboboxProps,
      | 'onChange'
      | 'defaultSelectedValue'
      | 'multiple'
      | 'kind'
      | 'selectedValue'
      | 'onSelectedValueChange'
      | 'renderSelectedValue'
      | 'renderPrefix'
      | 'ref'
    >,
    UseControllerComponentProps {
  label?: string;
  loading?: boolean;
  onChange?: (value: ComboboxValue<T>) => void;
  width?: string;
  hideError?: boolean;
  kind?: T;
  renderSelectedValue?: ComboboxRenderSelectedValue<T>;
  /**
   * Allow users to input a value that is not in the list. Also causes the value to not reset on blur.
   * @default false
   */
  freeForm?: boolean;
}

export const ControlledCombobox = <T extends 'single' | 'multiple' = 'single'>({
  items = [],
  label,
  loading,
  onChange,
  width,
  hideError = false,
  useControllerProps,
  formFieldProps,
  kind = 'single' as T,
  renderSelectedValue,
  freeForm = false,
  ...comboboxProps
}: Props<T>) => {
  const {
    field: { onBlur, onChange: onChangeControl, value },
    fieldState: { error },
  } = useController(useControllerProps);
  const [dispValue, setDispValue] = useState(value);

  const handleSelectedValueChange = (newValue: string | string[]) => {
    setDispValue(newValue);
    onChange?.(newValue as ComboboxValue<T>);
    onChangeControl(newValue);
  };

  const handleTempValueChange = (newValue: string) => {
    // In freeForm, we set form value to enable custom values.
    if (freeForm) {
      handleSelectedValueChange(newValue);
    } else {
      setDispValue(newValue);
    }
  };
  return (
    <FormField
      name={useControllerProps.name}
      slotLabel={label}
      slotError={hideError ? undefined : error?.message}
      status={error && 'error'}
      {...formFieldProps}
    >
      {({ status, ...args }) => {
        const baseProps = {
          status,
          style: { width },
          id: useControllerProps.name,
          name: useControllerProps.name,
          items,
          value: kind === 'multiple' ? '' : dispValue || '',
          onValueChange: handleTempValueChange,
          onBlur,
          slotEnd: loading && <TextInputSpinner />,
          resetValueOnBlur: !freeForm,
          ...comboboxProps,
          attributes: {
            ComboboxTrigger: {
              ...args,
              spellCheck: false,
              ...comboboxProps?.attributes?.ComboboxTrigger,
            },
          },
        };

        if (kind === 'multiple') {
          return (
            <Combobox
              {...baseProps}
              kind="multiple"
              selectedValue={value as string[]}
              onSelectedValueChange={(newValue: string[]) => handleSelectedValueChange(newValue)}
              renderSelectedValue={
                renderSelectedValue as
                  | ((args: {
                      selectedValue: string[];
                      setSelectedValue: (value: string[]) => void;
                    }) => ReactNode)
                  | undefined
              }
            />
          );
        } else {
          return (
            <Combobox
              {...baseProps}
              kind="single"
              selectedValue={value as string}
              onSelectedValueChange={(newValue: string) => handleSelectedValueChange(newValue)}
              renderSelectedValue={
                renderSelectedValue as
                  | ((args: {
                      selectedValue: string;
                      setSelectedValue: (value: string) => void;
                    }) => ReactNode)
                  | undefined
              }
            />
          );
        }
      }}
    </FormField>
  );
};
