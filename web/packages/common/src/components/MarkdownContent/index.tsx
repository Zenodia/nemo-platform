// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { markdownComponents } from '@nemo/common/src/components/MarkdownContent/components/markdownComponents';
import { remarkCallouts } from '@nemo/common/src/components/MarkdownContent/remarkCallouts';
import cn from 'classnames';
import { type FC } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export interface MarkdownContentProps {
  content: string;
  className?: string;
}

export const MarkdownContent: FC<MarkdownContentProps> = ({ content, className }) => {
  return (
    <div className={cn('max-w-none', className)}>
      <Markdown
        remarkPlugins={[remarkGfm, remarkCallouts]}
        skipHtml
        components={markdownComponents}
      >
        {content}
      </Markdown>
    </div>
  );
};
