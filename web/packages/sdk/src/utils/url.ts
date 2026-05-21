/*
 * SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

export const isUnroutableHost = (url: string): boolean => {
  try {
    const host = new URL(url).hostname.replace(/^\[|\]$/g, '');
    return host === '0.0.0.0' || host === '::' || host === '0:0:0:0:0:0:0:0';
  } catch {
    return false;
  }
};

export const resolveBrowserBaseUrl = (envValue: string | undefined): string => {
  if (envValue && !isUnroutableHost(envValue)) return envValue;
  return typeof window !== 'undefined' ? window.location.origin : '';
};
