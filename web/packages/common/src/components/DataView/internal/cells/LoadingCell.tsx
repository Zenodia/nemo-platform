// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Skeleton } from '@nvidia/foundations-react-core';
import { useState, type JSX } from 'react';

/** A plugin cell that renders a loading state. Used for the loading state of a table. */
export function LoadingCell(): JSX.Element {
  const [width] = useState(() => Math.floor(Math.random() * 40 + 60));
  return (
    <Skeleton
      suppressHydrationWarning
      // eslint-disable-next-line no-restricted-syntax -- random width per skeleton row
      style={{ width: `${width}%` }}
    />
  );
}
