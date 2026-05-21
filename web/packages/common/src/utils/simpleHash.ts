// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// Fast hash function for generating stable keys
export const simpleHash = (str: string): string => {
  const truncated = str.slice(0, 60);
  let hash = 0;
  for (let i = 0; i < truncated.length; i++) {
    const char = truncated.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(36);
};
