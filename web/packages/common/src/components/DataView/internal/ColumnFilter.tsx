// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DebouncedTextInput } from '@nemo/common/src/components/DataView/internal/DebouncedTextInput';
import type {
  FilterValue,
  IntentionalAny,
  MultiState,
} from '@nemo/common/src/components/DataView/internal/types';
import {
  Button,
  DropdownCheckboxItem,
  DropdownItem,
  DropdownRadioGroup,
  DropdownRadioGroupItem,
  Spinner,
} from '@nvidia/foundations-react-core';
import type { Column } from '@tanstack/react-table';
import { Fragment, useCallback, useState, type JSX } from 'react';

interface UseFilterStateResult {
  onChange: (value: FilterValue) => void;
  onMultiValueChange: (value: string) => void;
  value: FilterValue;
}

function useFilterState(defaultValue: FilterValue): UseFilterStateResult {
  const [value, setValue] = useState<FilterValue>(defaultValue);
  const onMultiValueChange = useCallback((next: string) => {
    setValue((_prev) => {
      const prev = (_prev as MultiState | undefined) ?? {};
      if (prev[next]) {
        const rest = { ...prev };
        delete rest[next];
        return rest;
      }
      return { ...prev, [next]: true };
    });
  }, []);
  return {
    onChange: setValue as UseFilterStateResult['onChange'],
    onMultiValueChange,
    value,
  };
}

export function ColumnFilter({
  column,
  onClose,
}: {
  column: Column<IntentionalAny>;
  onClose?: () => void;
}): JSX.Element | null {
  const { onChange, onMultiValueChange, value } = useFilterState(
    column.getFilterValue() as FilterValue
  );
  const filter = column.columnDef.meta?.filter;
  if (!filter) {
    return null;
  }
  if (filter.loading) {
    return (
      <div className="p-3">
        <Spinner description="Loading filters..." size="small" />
      </div>
    );
  }
  let filterComponent: JSX.Element | JSX.Element[] | undefined;
  if (filter.type === 'text') {
    filterComponent = (
      <DropdownItem
        className="nv-density-compact hover:!cursor-default hover:!bg-inherit"
        onSelect={(e) => e.preventDefault()}
        onPointerLeave={(e) => e.preventDefault()}
        onPointerMove={(e) => e.preventDefault()}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            const inputValue = (e.target as HTMLInputElement).value;
            column.setFilterValue(inputValue || undefined);
            onClose?.();
          }
        }}
      >
        <DebouncedTextInput
          onValueChange={onChange as (v: string) => void}
          placeholder={filter.placeholder || 'Filter'}
          size="small"
          value={(value as string | undefined) ?? ''}
        />
      </DropdownItem>
    );
  } else if (filter.type === 'boolean') {
    const filterValue = value as MultiState | undefined;
    filterComponent = ['True', 'False', 'Blank'].map((v) => (
      <DropdownCheckboxItem
        key={v}
        checked={filterValue?.[v] ?? false}
        onCheckedChange={() => onMultiValueChange(v)}
      >
        {v}
      </DropdownCheckboxItem>
    ));
  } else if (filter.type === 'custom') {
    filterComponent = filter.renderFilter({ column, setValue: onChange, value });
  } else if (filter.type === 'single-select') {
    const filterOptions = filter.options ?? filter.optionsBuilder?.(column);
    if (!filterOptions) {
      console.error(
        `DataView: Auto-generating options for column ${column.id} failed. Please provide options for the filter.`
      );
    } else {
      filterComponent = (
        <div className="size-full max-h-[var(--radix-dropdown-menu-content-available-height)] overflow-y-auto">
          <DropdownRadioGroup
            name="filter"
            onValueChange={onChange as (v: string) => void}
            value={value as string | undefined}
          >
            {filterOptions.map((item) => (
              <DropdownRadioGroupItem key={item.value} disabled={item.disabled} value={item.value}>
                {item.label ?? item.value.toString()}
              </DropdownRadioGroupItem>
            ))}
          </DropdownRadioGroup>
        </div>
      );
    }
  } else if (filter.type === 'multi-select') {
    const filterOptions = filter.options ?? filter.optionsBuilder?.(column);
    if (!filterOptions) {
      console.error(
        `DataView: Auto-generating options for column ${column.id} failed. Please provide options for the filter.`
      );
    } else {
      filterComponent = (
        <div className="size-full max-h-[var(--radix-dropdown-menu-content-available-height)] overflow-y-auto">
          {filterOptions.map((item) => (
            <DropdownCheckboxItem
              key={item.value}
              checked={(value as MultiState | undefined)?.[item.value] ?? false}
              disabled={item.disabled}
              onCheckedChange={() => onMultiValueChange(item.value)}
            >
              {item.label ?? item.value}
            </DropdownCheckboxItem>
          ))}
        </div>
      );
    }
  }
  return (
    <Fragment>
      {filterComponent}
      <DropdownItem
        className="nv-density-compact"
        onSelect={() => {
          const isEmpty = !value || (typeof value === 'object' && Object.keys(value).length === 0);
          column.setFilterValue(isEmpty ? undefined : value);
        }}
        filterValue=""
      >
        <Button className="!w-full text-nowrap" size="small" kind="secondary">
          Apply Filter
        </Button>
      </DropdownItem>
    </Fragment>
  );
}
