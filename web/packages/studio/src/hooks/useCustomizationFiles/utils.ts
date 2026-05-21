// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { FILESET_URI_PREFIX } from '@studio/hooks/useCustomizationFiles/constants';

export function parseFilesetUri(uri: string): { workspace: string; name: string } {
  const stripped = uri.startsWith(FILESET_URI_PREFIX) ? uri.slice(FILESET_URI_PREFIX.length) : uri;
  const [workspace = '', name = ''] = stripped.split('/');
  return { workspace, name };
}
