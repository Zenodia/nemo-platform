// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { OverflowGroup } from '@nemo/common/src/components/OverflowGroup';
import { Button, Flex } from '@nvidia/foundations-react-core';
import React, { ComponentProps, useRef } from 'react';

export const TagOverflowGroup = ({
  resetFilters,
  clearButtonText = 'Clear Filters',
  children,
  attributes,
}: {
  resetFilters: () => void;
  clearButtonText?: string;
  children: React.ReactNode;
  attributes?: {
    overflowGroup: ComponentProps<typeof OverflowGroup>;
  };
}) => {
  // Use a counter-based key that increments when children reference changes.
  // This forces OverflowGroup to re-mount when children content changes,
  // working around a bug where OverflowGroup only checks children count, not content.
  // Temporary fix until KUI fixes the issue.
  const prevChildrenRef = useRef(children);
  const keyCounterRef = useRef(0);

  if (prevChildrenRef.current !== children) {
    keyCounterRef.current += 1;
    prevChildrenRef.current = children;
  }

  return (
    <div className="w-full">
      <OverflowGroup
        {...attributes?.overflowGroup}
        key={keyCounterRef.current}
        lines={1}
        renderSeeMoreButton={({
          hiddenChildren,
          isHiddenChildrenExpanded,
          setIsHiddenChildrenExpanded,
          ref,
        }) => (
          // Render Clear Filter twice, one outside the overflow and one inside the 'Show More' element,
          // and conditionally show one or the other. This is to allow to show a "trailing" Clear Filter button.
          // The ref is for a Button; we attach it to Flex so the overflow group can measure it.
          <Flex ref={ref as unknown as React.Ref<HTMLDivElement>}>
            <Button
              kind="tertiary"
              size="small"
              onClick={() => setIsHiddenChildrenExpanded(!isHiddenChildrenExpanded)}
            >
              {isHiddenChildrenExpanded ? 'Show Less' : `+${hiddenChildren.length - 1} more`}
            </Button>
            {!isHiddenChildrenExpanded && (
              <Button kind="tertiary" size="small" onClick={resetFilters}>
                {clearButtonText}
              </Button>
            )}
          </Flex>
        )}
      >
        {children}
        <Button size="small" kind="tertiary" onClick={resetFilters}>
          {clearButtonText}
        </Button>
      </OverflowGroup>
    </div>
  );
};
