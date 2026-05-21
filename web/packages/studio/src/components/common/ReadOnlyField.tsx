// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Flex, Text } from '@nvidia/foundations-react-core';
import { FC, ReactNode } from 'react';

export interface ReadOnlyFieldProps {
  label: string;
  value: ReactNode;
  className?: string;
  /** Vertical alignment of label and value. Defaults to "start" for better multi-line content support */
  align?: 'start' | 'center' | 'end';
}

// TODO: Remove this component in issue #1132
/**
 * A reusable component for displaying label/value pairs in read-only mode.
 * Uses tabular layout with fixed label width and aligned values.
 *
 * @deprecated Use KVPair from @nemo/common instead. This component will be removed in a future release.
 * Import: `import { KVPair } from '@nemo/common/src/components/KVPair';`
 */
export const ReadOnlyField: FC<ReadOnlyFieldProps> = ({
  label,
  value,
  className,
  align = 'start',
}) => {
  return (
    <Flex align={align} gap="density-md" className={className}>
      <Text kind="label/regular/md" className="text-subtle w-[140px] flex-shrink-0">
        {label}
      </Text>
      <Text kind="body/regular/md" className="text-wrap">
        {value || '-'}
      </Text>
    </Flex>
  );
};
