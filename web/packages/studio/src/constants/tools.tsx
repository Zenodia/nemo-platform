// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Button, PageHeader } from '@nvidia/foundations-react-core';
import { ReactNode } from 'react';

/**
 * A collection of functions that can be used in a chat completion.
 * These are allowlisted tools that are avaiable for the Studio App to use.
 * The return type is a ReactNode because the tool call is rendered in the UI.
 */
export const tools: Record<string, (parameters: unknown) => ReactNode> = {
  get_weather: (): string => {
    return "I don't know the weather, what do I look like?";
  },
  rich_content: (parameters: unknown): ReactNode => {
    const props = parameters as { name: string; props: Record<string, unknown> };
    if (props.name === 'Button') {
      return <Button {...props.props} />;
    }
    if (props.name === 'Header') {
      return <PageHeader slotHeading={undefined} {...props.props} />;
    }
    return null;
  },
};
