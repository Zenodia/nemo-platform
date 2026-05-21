// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Flex, Text } from '@nvidia/foundations-react-core';
import { CircleAlert as ErrorIcon } from 'lucide-react';
import { FC } from 'react';

interface Props {
  message: string;
}
export const AnnotationErrorMessage: FC<Props> = ({ message }) => {
  return (
    <Flex align="center" gap="2">
      <ErrorIcon width={16} height={16} className="text-feedback-danger flex-shrink-0" />
      <Text kind="body/regular/sm" className="text-feedback-danger">
        {message}
      </Text>
    </Flex>
  );
};
