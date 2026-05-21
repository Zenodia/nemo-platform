// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * @deprecated This utility is no longer needed with v2 fileset APIs.
 * The v2 APIs handle storage internally - you work directly with workspace/name.
 */
export function isDataStoreUrl(url: string): boolean {
  return url.startsWith('hf://');
}

/**
 * @deprecated This utility is no longer needed with v2 fileset APIs.
 * Just use file.name directly.
 */
export function getFilePath(file: File): string {
  return file.name;
}
