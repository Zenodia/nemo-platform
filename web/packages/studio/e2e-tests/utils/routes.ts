// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { STUDIO_URL_BASE_PATH } from '@e2e-tests/utils/environment';

/**
 * Strips the base path from the given path. This is useful for comparing paths in environments
 * where Studio's base URL contains a path, like http://localhost:8080/studio/
 * @param path - The path to strip the base path from
 * @returns The path with the base path stripped
 */
export const stripBasePath = (path: string) => {
  if (!STUDIO_URL_BASE_PATH) {
    return path;
  }
  const stripped = path.replace(STUDIO_URL_BASE_PATH, '');
  return stripped.startsWith('/') ? stripped : `/${stripped}`;
};
