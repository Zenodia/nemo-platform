// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { TagOverflowGroup } from '@nemo/common/src/components/TagOverflowGroup';
import { formatDateRange } from '@nemo/common/src/utils/formatDateRange';
import { removeEmptyValues } from '@nemo/common/src/utils/removeEmptyValues';
import { Tag } from '@nvidia/foundations-react-core';
import { DatasetFilterState } from '@studio/routes/FilesetListRoute/types';
import { X } from 'lucide-react';
import type { Dispatch, FC, SetStateAction } from 'react';

type Props = {
  filterState: DatasetFilterState;
  setFilterState: Dispatch<SetStateAction<DatasetFilterState>>;
  resetFilters: () => void;
};

export const FilterTags: FC<Props> = ({ resetFilters, filterState, setFilterState }) => {
  const createRemoveFilterHandler = (fieldName: string) => () =>
    setFilterState(
      (curr) =>
        removeEmptyValues({
          ...curr,
          filter: {
            ...(curr.filter || {}),
            [fieldName]: undefined,
          },
        }) as DatasetFilterState
    );

  const storageTypeLabel =
    filterState?.filter?.storage_type === 'local'
      ? 'Local'
      : filterState?.filter?.storage_type === 'ngc'
        ? 'NGC'
        : filterState?.filter?.storage_type === 'huggingface'
          ? 'Hugging Face'
          : filterState?.filter?.storage_type === 's3'
            ? 'S3'
            : filterState?.filter?.storage_type;

  return (
    <TagOverflowGroup resetFilters={resetFilters}>
      {(filterState?.filter?.created_at?.$gte || filterState?.filter?.created_at?.$lte) && (
        <Tag onClick={createRemoveFilterHandler('created_at')} kind="outline" color="gray">
          Created:{' '}
          {formatDateRange(
            filterState?.filter?.created_at?.$gte,
            filterState?.filter?.created_at?.$lte
          )}
          <X />
        </Tag>
      )}
      {filterState?.filter?.storage_type && (
        <Tag onClick={createRemoveFilterHandler('storage_type')} kind="outline" color="gray">
          Storage Backend: {storageTypeLabel}
          <X />
        </Tag>
      )}
    </TagOverflowGroup>
  );
};
