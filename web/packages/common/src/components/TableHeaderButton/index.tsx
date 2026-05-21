// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Button, type ButtonProps } from '@nvidia/foundations-react-core';

export type TableHeaderButtonProps = Omit<ButtonProps, 'kind' | 'size'>;

/**
 * An accessible button component designed for use in table headers,
 * particularly for sortable columns. It applies some padding magic
 * so that the text aligns properly while still maintaining the ergonomic
 * clickable area.
 *
 * @example
 * ```tsx
 * // Basic sortable header
 * <TableHeaderButton
 *   onClick={() => handleSort('name')}
 *   aria-label="Sort by name"
 * >
 *   Name
 * </TableHeaderButton>
 * ```
 */
export function TableHeaderButton({ children, className, ...props }: TableHeaderButtonProps) {
  return (
    <Button
      kind="tertiary"
      className={`text-inherit font-inherit px-(--table-cell-inline-padding) -mx-(--table-cell-inline-padding) ${className || ''}`}
      {...props}
    >
      {children}
    </Button>
  );
}
