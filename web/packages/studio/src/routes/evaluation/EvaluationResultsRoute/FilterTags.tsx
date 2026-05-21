// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { TagOverflowGroup } from '@nemo/common/src/components/TagOverflowGroup';
import { formatDateRange } from '@nemo/common/src/utils/formatDateRange';
import { removeEmptyValues } from '@nemo/common/src/utils/removeEmptyValues';
import { Tag } from '@nvidia/foundations-react-core';
import type { EvaluationResultsFilterState } from '@studio/routes/evaluation/EvaluationResultsRoute/types';
import { X } from 'lucide-react';
import type { Dispatch, FC, SetStateAction } from 'react';

type Props = {
  filterState: EvaluationResultsFilterState;
  setFilterState: Dispatch<SetStateAction<EvaluationResultsFilterState>>;
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
        }) as EvaluationResultsFilterState
    );

  const selectedStatuses = filterState?.filter?.status ?? [];

  return (
    <TagOverflowGroup resetFilters={resetFilters}>
      {selectedStatuses.length > 0 && (
        <Tag onClick={createRemoveFilterHandler('status')} kind="outline" color="gray">
          Status: {selectedStatuses.map((s) => s.charAt(0).toUpperCase() + s.slice(1)).join(', ')}
          <X />
        </Tag>
      )}
      {(filterState?.filter?.created_at?.$gte || filterState?.filter?.created_at?.$lte) && (
        <Tag onClick={createRemoveFilterHandler('created_at')} color="gray" kind="outline">
          Created:{' '}
          {formatDateRange(
            filterState?.filter?.created_at?.$gte,
            filterState?.filter?.created_at?.$lte
          )}
          <X />
        </Tag>
      )}
    </TagOverflowGroup>
  );
};
