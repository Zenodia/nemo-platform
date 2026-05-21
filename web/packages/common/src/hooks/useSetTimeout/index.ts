// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useCallback, useEffect, useRef } from 'react';

/**
 * A function that works like native setTimeout but stores the timeout ID internally
 */
type SetTimeoutFn = (callback: () => void, delay: number) => void;

/**
 * A function that clears the stored timeout without needing a timeout ID parameter
 */
type ClearTimeoutFn = () => void;

/**
 * Custom React hook that provides a wrapped setTimeout function with automatic cleanup.
 *
 * This hook returns a tuple containing a wrapped setTimeout function and a clear function.
 * The wrapped setTimeout automatically manages the timeout ID and ensures cleanup on unmount.
 * If setTimeout is called multiple times, only the latest timeout is tracked and managed.
 *
 * @returns A tuple [setTimeoutFn, clearTimeoutFn]
 *
 * @example
 * ```typescript
 * const [setTimeoutFn, clearTimeoutFn] = useSetTimeout();
 *
 * // Use it like native setTimeout
 * setTimeoutFn(() => {
 *   console.log('Done!');
 * }, 5000);
 *
 * // Clear it without needing the timeout ID
 * clearTimeoutFn();
 *
 * // Automatically cleans up on unmount
 * ```
 */
export const useSetTimeout = (): [SetTimeoutFn, ClearTimeoutFn] => {
  const timeoutIdRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearTimeoutFn = useCallback<ClearTimeoutFn>(() => {
    if (timeoutIdRef.current !== null) {
      clearTimeout(timeoutIdRef.current);
      timeoutIdRef.current = null;
    }
  }, []);

  const setTimeoutFn = useCallback<SetTimeoutFn>(
    (callback: () => void, delay: number) => {
      // Clear any existing timeout first
      clearTimeoutFn();

      // Set new timeout and store ID
      timeoutIdRef.current = setTimeout(callback, delay);
    },
    [clearTimeoutFn]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearTimeoutFn();
    };
  }, [clearTimeoutFn]);

  return [setTimeoutFn, clearTimeoutFn];
};
