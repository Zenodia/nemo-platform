// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Block, Pagination } from '@nvidia/foundations-react-core';
import { ComponentProps } from 'react';

// TODO: Refactor this and upstream components to use API Context to remove prop drilling
export const StudioDataGridPagination = (
  paginationProps: Pick<
    ComponentProps<typeof Pagination>,
    'page' | 'pageSize' | 'pageSizeOptions' | 'totalItems' | 'onPageSizeChange'
  >
) => {
  return (
    <Block paddingTop="density-md" paddingBottom="density-sm">
      <Pagination
        {...paginationProps}
        displayControls
        kind="tabs"
        totalItems={paginationProps.totalItems}
        onPageSizeChange={paginationProps.onPageSizeChange}
      />
    </Block>
  );
};
