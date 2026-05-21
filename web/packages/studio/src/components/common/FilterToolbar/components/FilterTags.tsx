// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  Button,
  type DropdownEntry,
  type DropdownRadioGroupEntry,
  Stack,
  Tag,
} from '@nvidia/foundations-react-core';
import { X } from 'lucide-react';
import { FC } from 'react';

interface Props {
  filters: DropdownEntry[];
  onRemoveAllFilters: () => void;
}

export const FilterTags: FC<Props> = ({ filters, onRemoveAllFilters }) => {
  const hasAppliedFilter = !!filters.length;

  return (
    <Stack gap="density-sm" align="center" direction="row">
      {filters
        .filter((filter) => typeof filter !== 'string' && filter.kind === 'radio')
        .map((filter: DropdownRadioGroupEntry) => {
          if (Array.isArray(filter.value)) {
            return filter.value.map((value) => (
              <Tag
                key={`${filter.slotHeading}_${value}`}
                onClick={() => filter.onValueChange?.('')}
                kind="outline"
                color="gray"
              >
                {filter.slotHeading}: {value}
                <X fontSize="small" />
              </Tag>
            ));
          }
          return (
            <Tag
              key={`${filter.slotHeading}_${filter.value}`}
              onClick={() => filter.onValueChange?.('')}
              kind="outline"
              color="gray"
            >
              {filter.slotHeading}: {filter.value?.toString()}
              <X fontSize="small" />
            </Tag>
          );
        })}
      {hasAppliedFilter && (
        <Button kind="tertiary" size="small" onClick={onRemoveAllFilters}>
          <X />
          Clear All Filters
        </Button>
      )}
    </Stack>
  );
};
