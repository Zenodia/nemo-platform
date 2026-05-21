// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { FileSampleMethod } from '@nemo/common/src/utils/sampleTextLines';
import { Stack, Text } from '@nvidia/foundations-react-core';
import type { Meta, StoryObj } from '@storybook/react';
import { FileSamplingMethodSelect } from '@studio/components/FileSamplingSnippet/FileSamplingMethodSelect';
import { type FC, useState } from 'react';

/** Meta without `component` so interactive demos can use local state without dummy `args`. */
const meta = {
  title: 'Components/File Sampling/Method Select',
  parameters: { layout: 'padded' },
} satisfies Meta;

export default meta;

type Story = StoryObj<typeof meta>;

const MethodOnlyDemo: FC = () => {
  const [method, setMethod] = useState<FileSampleMethod>('random');
  return (
    <Stack gap="density-md" className="max-w-md">
      <FileSamplingMethodSelect value={method} onValueChange={setMethod} />
      <Text kind="body/regular/sm" className="text-secondary">
        Selected: <code className="font-mono">{method}</code>
      </Text>
    </Stack>
  );
};

/** Random / Head / Tail only (no row-count group). */
export const MethodOnly: Story = {
  name: 'Method only',
  render: () => <MethodOnlyDemo />,
};

const GroupedDemo: FC = () => {
  const [method, setMethod] = useState<FileSampleMethod>('head');
  const [maxRows, setMaxRows] = useState(10);
  return (
    <Stack gap="density-md" className="max-w-xl">
      <FileSamplingMethodSelect
        value={method}
        onValueChange={setMethod}
        rowCountGroup={{
          value: maxRows,
          onValueChange: setMaxRows,
          maxRows: 42,
        }}
      />
      <Text kind="body/regular/sm" className="text-secondary">
        Method <code className="font-mono">{method}</code>, max rows{' '}
        <code className="font-mono">{maxRows}</code> (dataset has 42 rows in this example).
      </Text>
    </Stack>
  );
};

/** Method select plus “Max rows” preset dropdown in one bordered group. */
export const WithRowCountGroup: Story = {
  name: 'With row count group',
  render: () => <GroupedDemo />,
};

const DisabledDemo: FC = () => (
  <FileSamplingMethodSelect
    value="tail"
    onValueChange={() => {}}
    rowCountGroup={{
      value: 25,
      onValueChange: () => {},
      maxRows: 100,
      disabled: true,
    }}
    attributes={{ select: { disabled: true } }}
  />
);

/** Disabled interaction (e.g. while inference runs). */
export const Disabled: Story = {
  name: 'Disabled',
  render: () => <DisabledDemo />,
};
