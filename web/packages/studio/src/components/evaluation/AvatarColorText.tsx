// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Avatar, Flex } from '@nvidia/foundations-react-core';
import { FC, PropsWithChildren } from 'react';

interface AvatarColorTextProps {
  color?: string;
  className?: string;
  title?: string;
  onClick?: () => void;
}

/**
 * A component that displays an avatar with a color indicator next to text content.
 * Used in evaluation comparisons to visually distinguish between different models.
 */
export const AvatarColorText: FC<PropsWithChildren<AvatarColorTextProps>> = ({
  className,
  color,
  children,
  title,
  onClick,
}) => {
  return (
    <Flex
      gap="density-sm"
      align="center"
      className={`truncate rounded ${className}`}
      title={title}
      onClick={onClick}
    >
      <Avatar
        className="h-[12px] w-[12px]"
        // eslint-disable-next-line no-restricted-syntax
        style={{ backgroundColor: color ?? 'transparent' }}
        fallback={null}
      />
      {children}
    </Flex>
  );
};
