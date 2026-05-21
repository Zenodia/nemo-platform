// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type {
  DataViewColumn,
  MultiState,
} from '@nemo/common/src/components/DataView/FilterPanel/types';
import { useMultiToggle } from '@nemo/common/src/components/DataView/FilterPanel/useMultiToggle';
import { Flex, Stack, Switch, Text } from '@nvidia/foundations-react-core';

export function BooleanFilterControl({ column }: { column: DataViewColumn }) {
  const value = column.getFilterValue() as MultiState | undefined;
  const toggle = useMultiToggle(column);

  return (
    <Stack gap="density-md">
      {(['True', 'False', 'Blank'] as const).map((label) => (
        <Flex key={label} align="center" justify="between" gap="2">
          <Text kind="body/regular/md">{label}</Text>
          <Switch
            data-testid={`column-filter-${column.id}-${label.toLowerCase()}`}
            checked={value?.[label] ?? false}
            onCheckedChange={() => toggle(label)}
          />
        </Flex>
      ))}
    </Stack>
  );
}
