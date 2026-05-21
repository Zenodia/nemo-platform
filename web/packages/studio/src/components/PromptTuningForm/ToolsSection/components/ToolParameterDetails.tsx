// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ChatCompletionToolsParam } from '@nemo/common/src/zod/tools';
import { Flex, Stack, Text } from '@nvidia/foundations-react-core';

export const ToolParameterDetails = ({ tool }: { tool: ChatCompletionToolsParam }) => {
  if (!tool.function.parameters) {
    return <Text>No parameters defined</Text>;
  }

  const { properties, required = [] } = tool.function.parameters;
  const requiredArray = Array.isArray(required) ? required : [];

  if (!properties || Object.keys(properties).length === 0) {
    return <Text>No parameters defined</Text>;
  }

  return (
    <Stack gap="density-sm">
      {Object.entries(properties).map(([paramName, paramSchema]) => (
        <Flex key={paramName} direction="col" gap="density-xs">
          <Flex gap="density-sm" align="center">
            <Text kind="label/semibold/md">{paramName}</Text>
            {requiredArray.includes(paramName) && (
              <Text kind="label/regular/sm" className="text-feedback-danger">
                (Required)
              </Text>
            )}
          </Flex>
          <Flex direction="col" gap="density-xs" className="ml-md">
            <Text kind="label/regular/sm">Type: {paramSchema.type}</Text>
            {paramSchema.description && (
              <Text kind="label/regular/sm">{paramSchema.description}</Text>
            )}
          </Flex>
        </Flex>
      ))}
    </Stack>
  );
};
