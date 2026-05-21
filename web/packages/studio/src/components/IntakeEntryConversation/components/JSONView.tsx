// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Entry } from '@nemo/sdk/generated/platform/schema';
import { CodeSnippet } from '@nvidia/foundations-react-core';
import { FC } from 'react';

interface JSONViewProps {
  /** The intake entry to display as JSON */
  entry: Entry;
}

/**
 * Displays an intake entry as formatted JSON in a code snippet.
 *
 * Renders the complete entry object as pretty-printed JSON with syntax
 * highlighting. The code snippet is collapsible and shows 20 rows by default.
 *
 * @param props - Component props
 * @param props.entry - The intake entry to serialize and display
 * @returns A collapsible code snippet with formatted JSON
 */
export const JSONView: FC<JSONViewProps> = ({ entry }) => {
  const jsonData = JSON.stringify(entry, null, 2);

  return (
    <CodeSnippet value={jsonData} language="json" kind="block" collapsible rows={20} defaultOpen />
  );
};
