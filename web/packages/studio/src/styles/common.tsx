// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';

interface MaxLineContainerProps {
  lines?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

export function MaxLineContainer({ lines = 2, children, style, className }: MaxLineContainerProps) {
  const maxLineStyles: React.CSSProperties = {
    display: '-webkit-box',
    WebkitLineClamp: `${lines}`,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
    ...style,
  };
  return (
    // eslint-disable-next-line no-restricted-syntax
    <div style={maxLineStyles} className={className}>
      {children}
    </div>
  );
}

export const tooltipClassName =
  'whitespace-pre-wrap max-h-[600px] max-w-[400px] overflow-auto leading-normal font-normal';

export const tabsClassName = '[&_.nv-tabs-content]:p-0 [&_.nv-tabs-content]:overflow-auto';
