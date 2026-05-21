// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { CALLOUT_MARKER_PATTERN } from '@nemo/common/src/components/MarkdownContent/constants';
import { isCalloutKind } from '@nemo/common/src/components/MarkdownContent/utils';

// Minimal mdast shape — kept local so this file doesn't pull in `@types/mdast`
// or `unist-util-visit` as direct deps. The plugin only touches blockquotes
// and the first text node of their first paragraph.
interface MdastNode {
  type: string;
  value?: string;
  children?: MdastNode[];
  data?: { hProperties?: Record<string, unknown> };
}

const visitBlockquotes = (node: MdastNode, visit: (blockquote: MdastNode) => void): void => {
  if (node.type === 'blockquote') {
    visit(node);
  }

  if (!node.children) {
    return;
  }

  for (const child of node.children) {
    visitBlockquotes(child, visit);
  }
};

// Detects GitHub-style alert markers (`> [!NOTE]`, `> [!TIP]`, ...) at the
// start of a blockquote and tags the node with `data-callout="<kind>"` so the
// blockquote component handler can render a styled callout. Stripping the
// marker here removes the need for any React-tree post-processing downstream.
export const remarkCallouts = () => (tree: MdastNode) => {
  visitBlockquotes(tree, (blockquote) => {
    const firstParagraph = blockquote.children?.[0];
    if (firstParagraph?.type !== 'paragraph') {
      return;
    }

    const firstText = firstParagraph.children?.[0];
    if (firstText?.type !== 'text' || typeof firstText.value !== 'string') {
      return;
    }

    const match = firstText.value.match(CALLOUT_MARKER_PATTERN);
    if (!match) {
      return;
    }

    const kind = match[1].toLowerCase();
    if (!isCalloutKind(kind)) {
      return;
    }

    firstText.value = firstText.value.slice(match[0].length);
    blockquote.data ??= {};
    blockquote.data.hProperties ??= {};
    blockquote.data.hProperties.dataCallout = kind;
  });
};
