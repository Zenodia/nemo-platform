// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Button, type ButtonProps } from '@nvidia/foundations-react-core';
import { CircleCheck, RefreshCw } from 'lucide-react';
import type { JSX } from 'react';

/**
 * A refresh button for the table. If the table is fetching data, a spinner is displayed
 * instead. Intended for use within `DataView.Toolbar`.
 */
export function RefreshButton({
  disabled,
  isFetching,
  ...props
}: {
  /** Whether the table is fetching data. */
  isFetching: boolean;
  /** Function to call when the button is clicked. Should trigger a refetch of the table data. */
  onClick: () => void;
} & Omit<ButtonProps, 'onClick'>): JSX.Element {
  return (
    <Button
      aria-label={isFetching ? 'Loading data' : 'RefreshCw data'}
      disabled={disabled || isFetching}
      kind="tertiary"
      {...props}
    >
      {isFetching ? (
        <CircleCheck className="animate-spin" variant="fill" />
      ) : (
        <RefreshCw variant="fill" />
      )}
      <span className="hide-mobile">RefreshCw</span>
    </Button>
  );
}
