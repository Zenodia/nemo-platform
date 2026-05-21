// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Button, Popover } from '@nvidia/foundations-react-core';
import classnames from 'classnames';
import React, {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type ComponentPropsWithoutRef,
  type MouseEvent,
  type ReactNode,
} from 'react';

export interface OverflowGroupRenderSeeMoreButtonArgs {
  hiddenChildren: ReactNode[];
  isHiddenChildrenExpanded: boolean;
  setIsHiddenChildrenExpanded: (isHiddenChildrenExpanded: boolean) => void;
  ref: (element: HTMLButtonElement | null) => void;
}

export interface OverflowGroupProps extends ComponentPropsWithoutRef<'div'> {
  /**
   * If true, the overflow group will take the full width of its container.
   * @default true
   */
  fullWidth?: boolean;
  /** The gap between the children, in pixels. */
  gap?: number;
  /** The kind of overflow group. */
  kind?: 'expand' | 'popover';
  /**
   * The number of lines that can be visible before it's considered to overflow.
   * @default 1
   */
  lines?: number;
  /** Callback triggered when the default see more button is clicked. */
  onSeeMoreButtonClick?: (event: MouseEvent<HTMLButtonElement>) => void;
  /**
   * Render a custom see more component. Make sure to set the `ref` prop to the button
   * element so the `OverflowGroup` can correctly calculate its width.
   */
  renderSeeMoreButton?: (args: OverflowGroupRenderSeeMoreButtonArgs) => ReactNode;
  /** Render custom popover content. Receives the hidden children as an argument. */
  renderPopoverContent?: (children: ReactNode[]) => ReactNode;
}

export const OverflowGroupDefaults = {
  kind: 'expand',
  gap: 8,
  lines: 1,
  dataTestId: 'overflow-group',
} as const;

export function OverflowGroup({
  children,
  className = '',
  fullWidth = true,
  kind = OverflowGroupDefaults.kind,
  gap = OverflowGroupDefaults.gap,
  lines = OverflowGroupDefaults.lines,
  onSeeMoreButtonClick,
  renderSeeMoreButton,
  renderPopoverContent,
  ...props
}: OverflowGroupProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const measureRef = useRef<HTMLDivElement | null>(null);
  const [{ visibleChildren, hiddenChildren }, setOverflowChildren] = useState<{
    visibleChildren: ReactNode[];
    hiddenChildren: ReactNode[];
  }>({
    visibleChildren: [],
    hiddenChildren: [],
  });
  const [isHiddenChildrenExpanded, setIsHiddenChildrenExpanded] = useState(false);
  const [seeMoreButtonRef, setSeeMoreButtonRef] = useState<HTMLButtonElement | null>(null);

  const childrenArray = useMemo(() => React.Children.toArray(children), [children]);
  const childrenArrayRef = useRef(childrenArray);
  childrenArrayRef.current = childrenArray;

  const calculateVisibleItems = useCallback(() => {
    if (!containerRef.current || !measureRef.current || isHiddenChildrenExpanded) return;

    const containerWidth = containerRef.current.offsetWidth;
    const childElements = Array.from(measureRef.current.children) as HTMLElement[];
    const currentChildren = childrenArrayRef.current;
    let currentLine = 1;
    let currentLineWidth = 0;
    let visibleCount = 0;
    for (let i = 0; i < childElements.length; i++) {
      const child = childElements[i];
      const childWidth = child.offsetWidth + gap;
      const counterWidth =
        visibleCount < currentChildren.length - 1 ? (seeMoreButtonRef?.offsetWidth ?? 0) : 0;
      if (currentLineWidth + childWidth + counterWidth > containerWidth) {
        currentLine++;
        currentLineWidth = childWidth;
      } else {
        currentLineWidth += childWidth;
      }
      if (currentLine > lines) {
        break;
      }
      visibleCount++;
    }
    if (
      visibleCount !== visibleChildren.length ||
      currentChildren.length !== visibleChildren.length + hiddenChildren.length
    ) {
      setOverflowChildren({
        visibleChildren: currentChildren.slice(0, visibleCount),
        hiddenChildren: currentChildren.slice(visibleCount),
      });
    }
  }, [
    isHiddenChildrenExpanded,
    visibleChildren.length,
    hiddenChildren.length,
    gap,
    lines,
    seeMoreButtonRef?.offsetWidth,
  ]);

  useLayoutEffect(() => {
    calculateVisibleItems();
    const resizeObserver = new ResizeObserver(calculateVisibleItems);
    const container = containerRef.current;
    if (container) {
      resizeObserver.observe(container);
    }
    return () => {
      if (container) {
        resizeObserver.disconnect();
      }
    };
  }, [calculateVisibleItems]);

  useEffect(() => {
    calculateVisibleItems();
  }, [children, calculateVisibleItems]);

  const seeMoreButton = useMemo(
    () =>
      renderSeeMoreButton?.({
        hiddenChildren,
        isHiddenChildrenExpanded,
        setIsHiddenChildrenExpanded,
        ref: setSeeMoreButtonRef,
      }) ?? (
        <Button
          className="shrink-0"
          color="neutral"
          onClick={(e) => {
            onSeeMoreButtonClick?.(e);
            if (kind !== 'popover') {
              setIsHiddenChildrenExpanded((p) => !p);
            }
          }}
          ref={setSeeMoreButtonRef}
          kind="tertiary"
          size="small"
          title={
            isHiddenChildrenExpanded
              ? 'Click to show fewer items'
              : `Click to show ${hiddenChildren.length} more items`
          }
        >
          {isHiddenChildrenExpanded ? 'See Less' : `+${hiddenChildren.length}`}
        </Button>
      ),
    [renderSeeMoreButton, hiddenChildren, isHiddenChildrenExpanded, onSeeMoreButtonClick, kind]
  );

  const popoverContent = useMemo(
    () =>
      renderPopoverContent?.(hiddenChildren) ?? (
        <div
          className="flex max-w-full flex-wrap"
          // eslint-disable-next-line no-restricted-syntax -- gap is a dynamic numeric prop
          style={{ gap: `${gap}px` }}
        >
          {hiddenChildren}
        </div>
      ),
    [renderPopoverContent, hiddenChildren, gap]
  );

  return (
    <div
      className={classnames('relative', fullWidth && 'w-full', className)}
      data-has-overflow={hiddenChildren.length > 0}
      data-testid={OverflowGroupDefaults.dataTestId}
      {...props}
    >
      <div
        ref={containerRef}
        className={classnames(
          'flex items-center overflow-hidden [&>*]:shrink-0 [&>*]:whitespace-nowrap',
          (lines > 1 || isHiddenChildrenExpanded) && 'flex-wrap'
        )}
        data-testid="overflow-group-visible-children"
        // eslint-disable-next-line no-restricted-syntax -- gap is a dynamic numeric prop
        style={{ gap: `${gap}px` }}
      >
        {visibleChildren}
        {isHiddenChildrenExpanded && hiddenChildren}
        {hiddenChildren.length > 0 &&
          (kind === 'popover' ? (
            <Popover slotContent={popoverContent}>{seeMoreButton}</Popover>
          ) : (
            seeMoreButton
          ))}
      </div>
      <div
        ref={measureRef}
        className={classnames(
          'pointer-events-none absolute top-[-9999px] left-[-9999px] flex h-0 items-center opacity-0',
          lines > 1 && 'flex-wrap'
        )}
        data-testid="overflow-group-measurement-container"
        // eslint-disable-next-line no-restricted-syntax -- gap is a dynamic numeric prop
        style={{ gap: `${gap}px` }}
        aria-hidden="true"
        inert
      >
        {childrenArray.map((child, index) => (
          <div className="shrink-0" key={index}>
            {child}
          </div>
        ))}
      </div>
    </div>
  );
}
