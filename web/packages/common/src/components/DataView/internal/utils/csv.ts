// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { IntentionalAny } from '@nemo/common/src/components/DataView/internal/types';
import { childrenToText } from '@nvidia/foundations-react-core/lib';
import type { Column, Row } from '@tanstack/react-table';
import type { ReactNode } from 'react';

export function escapeCSV(value: string): string {
  const sanitized = /^[=+\-@]/.test(value.trimStart()) ? `'${value}` : value;
  if (/[,"\n\r]/.test(sanitized)) {
    return `"${sanitized.replace(/"/g, '""')}"`;
  }
  return sanitized;
}

export function generateCSV(
  rows: Row<IntentionalAny>[],
  columns: Column<IntentionalAny>[]
): string {
  const dataColumns = columns.filter((col) => !col.columnDef.meta?._isPrebuiltColumn);
  const headers = dataColumns.map((col) =>
    escapeCSV(childrenToText(col.columnDef.header as ReactNode))
  );
  const dataRows = rows.map((row) =>
    dataColumns.map((col) => escapeCSV(String(row.getValue(col.id) ?? '')))
  );
  return [headers, ...dataRows].map((row) => row.join(',')).join('\n');
}

export function downloadFile(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
