// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DateRangeFilterField } from '@nemo/common/src/components/FilterFields';
import { StorageConfigType } from '@nemo/sdk/generated/platform/schema';
import { Accordion, Flex, Select } from '@nvidia/foundations-react-core';
import { DatasetFilterState } from '@studio/routes/FilesetListRoute/types';
import { Dispatch, SetStateAction } from 'react';

interface Props {
  filterState: DatasetFilterState;
  setFilterState: Dispatch<SetStateAction<DatasetFilterState>>;
}

const STORAGE_BACKEND_OPTIONS = [
  { value: '', children: 'All' },
  { value: StorageConfigType.local, children: 'Local' },
  { value: StorageConfigType.ngc, children: 'NGC' },
  { value: StorageConfigType.huggingface, children: 'Hugging Face' },
  { value: StorageConfigType.s3, children: 'S3' },
];

export const FilterPanel = ({ filterState, setFilterState }: Props) => {
  return (
    <Accordion
      defaultValue={['created_at', 'storage_type']}
      multiple
      items={[
        {
          slotTrigger: (
            <Flex align="center" gap="2">
              Created
            </Flex>
          ),
          slotContent: (
            <DateRangeFilterField
              dataTestId="dataset-created-at-filter"
              value={filterState?.filter?.created_at}
              onValueChange={(value) => {
                setFilterState((curr) => ({
                  ...curr,
                  filter: {
                    ...(curr.filter || {}),
                    created_at: value,
                  },
                }));
              }}
            />
          ),
          value: 'created_at',
        },
        {
          slotTrigger: (
            <Flex align="center" gap="2">
              Storage Backend
            </Flex>
          ),
          slotContent: (
            <Select
              data-testid="dataset-storage-type-filter"
              placeholder="Select storage backend"
              value={filterState?.filter?.storage_type ?? ''}
              onValueChange={(value) => {
                const storageType =
                  typeof value === 'string' && value ? (value as StorageConfigType) : undefined;
                setFilterState((curr) => ({
                  ...curr,
                  filter: {
                    ...(curr.filter || {}),
                    storage_type: storageType,
                  },
                }));
              }}
              items={STORAGE_BACKEND_OPTIONS}
            />
          ),
          value: 'storage_type',
        },
      ]}
    />
  );
};
