// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export function getHeaderId(id: string, fromColumnId = false): string {
  if (fromColumnId) {
    return id.replace('data-view-column-', '');
  }
  return `data-view-column-${id}`;
}
