// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Flex, Stack, Text } from '@nvidia/foundations-react-core';

const SimpleModelDetailsDisplayItem = ({
  label,
  value,
}: {
  label: string;
  value: string | React.ReactNode | undefined;
}) => (
  <Flex direction="row" gap="density-sm">
    <Text kind="label/semibold/md" className="w-40 text-subtle" id={label}>
      {label}
    </Text>
    {!value ? (
      <Text kind="body/semibold/md" className="flex-1" aria-describedby={label}>
        -
      </Text>
    ) : typeof value === 'string' ? (
      <Text kind="body/semibold/md" className="flex-1" aria-describedby={label}>
        {value}
      </Text>
    ) : (
      value
    )}
  </Flex>
);

interface SimpleModelDetailsDisplayProps {
  modelName?: string;
  description?: string;
  baseModel?: string;
  temperature?: number;
  maxTokens?: number;
  systemPrompt?: string;
}
export const SimpleModelDetailsDisplay = ({
  modelName,
  description,
  baseModel,
  temperature,
  maxTokens,
  systemPrompt,
}: SimpleModelDetailsDisplayProps) => (
  <Stack gap="density-xl" className="w-full">
    <SimpleModelDetailsDisplayItem label="Model Name" value={modelName} />
    {description?.trim() && (
      <SimpleModelDetailsDisplayItem label="Description" value={description} />
    )}
    <SimpleModelDetailsDisplayItem label="Base Model" value={baseModel} />
    <SimpleModelDetailsDisplayItem
      label="Temperature"
      value={temperature != null && String(temperature)}
    />
    <SimpleModelDetailsDisplayItem
      label="Max Tokens"
      value={maxTokens != null && String(maxTokens)}
    />
    {systemPrompt?.trim() && (
      <SimpleModelDetailsDisplayItem
        label="System Prompt"
        value={
          <Text className="w-full min-h-min overflow-y-auto flex-1 border-base border rounded-md p-2">
            {systemPrompt}
          </Text>
        }
      />
    )}
  </Stack>
);
