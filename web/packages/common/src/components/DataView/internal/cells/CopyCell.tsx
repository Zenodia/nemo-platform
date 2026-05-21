// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { TSFixMe } from '@nemo/common/src/components/DataView/internal/types';
import { isCellContext } from '@nemo/common/src/components/DataView/internal/utils/cell-utils';
import { Tooltip } from '@nvidia/foundations-react-core';
import type { CellContext } from '@tanstack/react-table';
import { useCallback, useState, type ReactNode } from 'react';

type CellComponent<TData, TValue> = (ctx: CellContext<TData, TValue>) => TSFixMe;

function copyToClipboard(value: string | undefined): void {
  if (value) {
    navigator.clipboard.writeText(value);
  }
}

interface CopyButtonWrapperProps {
  children: ReactNode;
  value: string | undefined;
}

function CopyButtonWrapper({ children, value }: CopyButtonWrapperProps) {
  const [isCopied, setIsCopied] = useState(false);
  const handleClick = useCallback(() => {
    copyToClipboard(value);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 1000);
  }, [value]);
  return (
    <Tooltip
      slotContent={isCopied ? `Copied "${value}" to clipboard` : 'Click to copy'}
      open={isCopied ? isCopied : undefined}
    >
      <button
        className="hover:bg-interaction-hover inline-block max-w-full truncate border-none bg-transparent p-0 [text-align:inherit] transition-colors duration-250 ease-out select-text"
        onClick={handleClick}
      >
        {children}
      </button>
    </Tooltip>
  );
}

/**
 * Plugin cell that renders a copy button. Can wrap other cells, or be used directly as a cell.
 *
 * @example
 * ```tsx
 * columnHelper.accessor('id', { cell: CopyCell, header: 'ID' });
 * columnHelper.accessor('lastModified', { cell: CopyCell(DateCell), header: 'Last Modified' });
 * ```
 */
export function CopyCell<TData, TValue>(
  cellOrContext: CellComponent<TData, TValue> | CellContext<TData, TValue>
): TSFixMe {
  if (isCellContext<TData, TValue, CellComponent<TData, TValue>>(cellOrContext)) {
    const value = cellOrContext.getValue();
    return (
      <CopyButtonWrapper value={value as string | undefined}>
        {value as ReactNode}
      </CopyButtonWrapper>
    );
  }
  const CellWithCopy = (context: CellContext<TData, TValue>) => (
    <CopyButtonWrapper value={context.getValue() as string | undefined}>
      {cellOrContext(context) as ReactNode}
    </CopyButtonWrapper>
  );
  return CellWithCopy;
}
