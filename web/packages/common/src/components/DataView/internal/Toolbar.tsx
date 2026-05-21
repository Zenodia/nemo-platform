// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useInnerDataViewContext } from '@nemo/common/src/components/DataView/internal/context';
import { TableToolbar, type TableToolbarProps } from '@nvidia/foundations-react-core';
import classnames from 'classnames';
import type { JSX } from 'react';

/**
 * Renders the main toolbar in the DataView. Contains the search bar, view toggle, refresh
 * button, and other persistent controls.
 */
export function Toolbar({
  className,
  children,
  slotBulkActions,
  ...props
}: TableToolbarProps): JSX.Element {
  const { table } = useInnerDataViewContext();
  const hasSelectedRows = table.getSelectedRowModel().flatRows.length > 0;
  return (
    <TableToolbar
      aria-label="Data view toolbar"
      className={classnames(
        '@container relative [&_.hide-mobile]:@max-md:hidden [&_.only-mobile]:@md:hidden',
        className
      )}
      slotBulkActions={slotBulkActions}
      showBulkActionsToolbar={hasSelectedRows && Boolean(slotBulkActions)}
      {...props}
    >
      {children}
    </TableToolbar>
  );
}
