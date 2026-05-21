// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Block, Flex, Stack } from '@nvidia/foundations-react-core';
import { FC, PropsWithChildren } from 'react';

export const Panel: FC<PropsWithChildren<{ className?: string }>> = ({ children, className }) => (
  <Flex className={`h-full ${className || ''}`}>{children}</Flex>
);

export const PanelContent: FC<PropsWithChildren<{ className?: string }>> = ({
  children,
  className,
}) => (
  <Stack
    direction="col"
    align="start"
    justify="between"
    className={`flex flex-col h-full w-full overflow-hidden ${className || ''}`}
  >
    {children}
  </Stack>
);

export const PanelBody: FC<PropsWithChildren<{ className?: string }>> = ({
  children,
  className,
}) => (
  <Block
    className={`flex-1 min-h-0 w-full p-lg overflow-auto scrollbar-gutter-stable ${className || ''}`}
  >
    {children}
  </Block>
);

export const PanelFooter: FC<PropsWithChildren<{ className?: string }>> = ({
  children,
  className,
}) => (
  <Flex
    direction="row"
    gap="density-md"
    justify="between"
    padding="density-md"
    className={`w-full h-14 flex-none border-t-1 border-base ${className || ''}`}
  >
    {children}
  </Flex>
);
