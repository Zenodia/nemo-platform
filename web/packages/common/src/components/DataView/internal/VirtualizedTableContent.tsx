// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useInnerDataViewContext } from '@nemo/common/src/components/DataView/internal/context';
import { useMeasureInitialColumnWidthsOnMount } from '@nemo/common/src/components/DataView/internal/hooks/useMeasureInitialColumnWidthsOnMount';
import {
  TableContent,
  type TableContentProps,
} from '@nemo/common/src/components/DataView/internal/TableContent';
import { useVirtualizer, type VirtualizerOptions } from '@tanstack/react-virtual';
import classnames from 'classnames';
import { Fragment, useLayoutEffect, useMemo, useRef, type CSSProperties, type JSX } from 'react';

const DEFAULT_ROW_HEIGHT = 56;

const getMeasureElement = (): ((element: HTMLElement) => number) | undefined =>
  typeof window !== 'undefined' && navigator.userAgent.indexOf('Firefox') === -1
    ? (element) => element.getBoundingClientRect().height
    : undefined;

export type VirtualizedTableContentProps = Omit<TableContentProps, 'width' | 'virtualizer'> &
  (
    | {
        /** @deprecated Replace with `maxHeight` */
        height: CSSProperties['height'];
        maxHeight?: never;
      }
    | {
        height?: never;
        /** Virtualized content requires a height to limit it. */
        maxHeight: CSSProperties['maxHeight'];
      }
  ) & {
    /**
     * Number of additional hidden rows to add to the virtualized list. The current implementation
     * does not account for subrows; if you use subrows, set this to the max subrows expected.
     * @defaultValue 0
     */
    countOffset?: number;
    /**
     * Max number of rows to render to measure approximate column widths.
     * @defaultValue 5
     */
    measurementModeRows?: number;
    /**
     * Number of items to render outside of the visible window.
     * @defaultValue 5
     */
    overscan?: number;
    /** Height of each row in pixels. @defaultValue 56 */
    rowHeight?: number;
    /** Options to pass to the virtualizer. */
    virtualizeOptions?: VirtualizerOptions<HTMLTableElement, HTMLElement>;
    /** @deprecated Use `style` and CSS instead. */
    width?: CSSProperties['width'];
  };

/**
 * The DataView Virtualized Table content component. For non-virtualized tables, use `TableContent`.
 */
export function VirtualizedTableContent({
  className,
  countOffset = 0,
  height,
  maxHeight,
  measurementModeRows = 5,
  overscan = 5,
  rowHeight = DEFAULT_ROW_HEIGHT,
  stickyTableHeader = true,
  style,
  virtualizeOptions,
  width,
  ...props
}: VirtualizedTableContentProps): JSX.Element {
  const { table, totalCount } = useInnerDataViewContext();
  const tableContainerRef = useRef<HTMLTableElement | null>(null);
  const rowCount = table.getRowModel().rows.length;
  const rowVirtualizer = useVirtualizer({
    count: (totalCount ?? rowCount) + countOffset,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => rowHeight,
    measureElement: getMeasureElement(),
    overscan,
    ...virtualizeOptions,
  });
  const { measured, setMeasurementRef } = useMeasureInitialColumnWidthsOnMount({
    measurementModeRows,
  });

  useLayoutEffect(() => {
    if (!tableContainerRef.current) return;
    const tbody = tableContainerRef.current?.getElementsByTagName('tbody');
    rowVirtualizer.getVirtualItems().forEach((_, index) => {
      const element = tbody?.[0]?.children[index] as HTMLElement | undefined;
      if (element) {
        rowVirtualizer.measureElement(element);
      }
    });
  }, [rowVirtualizer, rowCount]);

  const stableStyle = useMemo(
    () => ({ maxHeight, height, width, ...style }),
    [maxHeight, height, width, style]
  );

  return (
    <Fragment>
      <TableContent
        className={classnames(
          className,
          'relative grid [grid-template-rows:min-content]',
          '[&_tbody]:relative [&_tbody_tr]:absolute [&_th]:flex [&_thead]:grid [&_thead_tr]:flex [&_tr]:w-full [&_tr]:empty:hidden'
        )}
        ref={tableContainerRef}
        virtualizer={rowVirtualizer}
        stickyTableHeader={stickyTableHeader}
        // eslint-disable-next-line no-restricted-syntax -- merged dynamic style
        style={stableStyle}
        {...props}
      />
      {!measured && measurementModeRows && (
        <div
          aria-hidden="true"
          className="pointer-events-none invisible h-0 w-full overflow-hidden opacity-0"
          inert
        >
          <TableContent
            className={classnames(className, 'overflow-scroll')}
            ref={setMeasurementRef}
            rowLimit={measurementModeRows}
            // eslint-disable-next-line no-restricted-syntax -- merged dynamic style
            style={stableStyle}
            {...props}
          />
        </div>
      )}
    </Fragment>
  );
}
