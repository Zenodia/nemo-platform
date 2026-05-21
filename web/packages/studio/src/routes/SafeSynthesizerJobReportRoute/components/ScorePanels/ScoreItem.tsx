// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Flex, Text } from '@nvidia/foundations-react-core';
import { CircleCheck, Ban } from 'lucide-react';
import { FC } from 'react';

interface ScoreItemProps {
  success: boolean;
  value: string;
}
export const ScoreItem: FC<ScoreItemProps> = ({ success, value }) => {
  return (
    <Flex align="center" gap="density-md">
      {success ? <CircleCheck className="text-brand" /> : <Ban />}
      <Text>{value}</Text>
    </Flex>
  );
};
