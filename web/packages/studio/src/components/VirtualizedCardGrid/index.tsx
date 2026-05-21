/*
 * SPDX-FileCopyrightText: Copyright (c) 2022-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
 */

import { Block, Spinner, Stack } from '@nvidia/foundations-react-core';
import { useColumnCount } from '@studio/hooks/useColumnCount';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useCallback, useEffect, useMemo, useRef, type ReactNode, type RefObject } from 'react';

const DEFAULT_GRID_CLASS =
  'grid grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 min-[2100px]:grid-cols-5! gap-6';
const DEFAULT_ESTIMATE_ROW_HEIGHT = 320;
const DEFAULT_ROW_GAP = 24; // matches gap-6 (1.5rem = 24px)
const LOAD_MORE_THRESHOLD = 3;

interface VirtualizedCardGridProps<T> {
  items: T[];
  renderCard: (item: T) => ReactNode;
  getItemKey: (item: T) => string;
  scrollContainerRef: RefObject<HTMLDivElement | null>;
  gridClassName?: string;
  estimateRowHeight?: number;
  rowGap?: number;
  hasMore?: boolean;
  onLoadMore?: () => Promise<void> | void;
}

export function VirtualizedCardGrid<T>({
  items,
  renderCard,
  getItemKey,
  scrollContainerRef,
  gridClassName = DEFAULT_GRID_CLASS,
  estimateRowHeight = DEFAULT_ESTIMATE_ROW_HEIGHT,
  rowGap = DEFAULT_ROW_GAP,
  hasMore = false,
  onLoadMore,
}: VirtualizedCardGridProps<T>) {
  const [columnCount, sizeProbeRef] = useColumnCount();
  const isLoadingRef = useRef(false);

  const rows = useMemo(() => {
    if (columnCount === 0) return [];
    const result: T[][] = [];
    for (let i = 0; i < items.length; i += columnCount) {
      result.push(items.slice(i, i + columnCount));
    }
    return result;
  }, [items, columnCount]);

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => scrollContainerRef.current,
    estimateSize: () => estimateRowHeight,
    overscan: 3,
    gap: rowGap,
  });

  const virtualItems = virtualizer.getVirtualItems();

  const loadMore = useCallback(() => {
    if (!hasMore || !onLoadMore || isLoadingRef.current) return;
    isLoadingRef.current = true;
    Promise.resolve(onLoadMore()).finally(() => {
      isLoadingRef.current = false;
    });
  }, [hasMore, onLoadMore]);

  useEffect(() => {
    if (virtualItems.length === 0) return;
    const lastRow = virtualItems[virtualItems.length - 1];
    if (lastRow.index >= rows.length - LOAD_MORE_THRESHOLD) {
      loadMore();
    }
  }, [virtualItems, rows.length, loadMore]);

  return (
    <Block className="relative">
      {/* Hidden sizer to determine column count from computed grid styles */}
      <div
        ref={sizeProbeRef}
        className={`${gridClassName} invisible absolute w-full h-0`}
        aria-hidden="true"
      />

      {/* eslint-disable-next-line no-restricted-syntax -- runtime pixel value from virtualizer; not expressible as a static Tailwind class */}
      <Stack className="relative w-full" style={{ height: virtualizer.getTotalSize() }}>
        {virtualItems.map((virtualRow) => (
          <Block
            key={virtualRow.key}
            ref={virtualizer.measureElement}
            data-index={virtualRow.index}
            className="absolute top-0 left-0 w-full"
            // eslint-disable-next-line no-restricted-syntax -- per-scroll translateY from virtualizer; not expressible as a static Tailwind class
            style={{ transform: `translateY(${virtualRow.start}px)` }}
          >
            <Block className={gridClassName}>
              {rows[virtualRow.index].map((item) => (
                <Block key={getItemKey(item)}>{renderCard(item)}</Block>
              ))}
            </Block>
          </Block>
        ))}
      </Stack>

      {hasMore && (
        <Block className="flex justify-center py-4">
          <Spinner aria-label="Loading more items" size="small" />
        </Block>
      )}
    </Block>
  );
}
