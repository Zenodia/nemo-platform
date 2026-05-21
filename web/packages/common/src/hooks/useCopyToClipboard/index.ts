// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useCallback } from 'react';

type UseCopyToClipboardProps = {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
};

interface UseCopyToClipboardResult {
  copyToClipboard: (content: string) => Promise<void>;
}

export const useCopyToClipboard = (
  opts: UseCopyToClipboardProps = {}
): UseCopyToClipboardResult => {
  const { onSuccess, onError } = opts;

  const copyToClipboard = useCallback(
    async (content: string): Promise<void> => {
      try {
        await navigator.clipboard.writeText(content);
        onSuccess?.();
      } catch (error) {
        console.error('Failed to copy text to clipboard', error);
        onError?.(error as Error);
      }
    },
    [onSuccess, onError]
  );

  return { copyToClipboard };
};
