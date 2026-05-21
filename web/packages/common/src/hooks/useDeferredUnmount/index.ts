// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useState, useRef, useEffect, useCallback } from 'react';

/**
 * Default delay before clearing the value after close (in milliseconds).
 * This matches typical CSS transition durations for smooth animations.
 */
const DEFAULT_DELAY = 300;

/**
 * Configuration options for the useDeferredUnmount hook.
 */
export interface UseDeferredUnmountOptions {
  /**
   * Delay in milliseconds before clearing the value after closing.
   * This should match your exit animation duration to ensure content
   * remains visible during the animation.
   * @default 300
   */
  delay?: number;
}

/**
 * Return type for the useDeferredUnmount hook.
 * @template T - The type of value being managed
 */
export interface UseDeferredUnmountReturn<T> {
  /**
   * Whether the panel/modal is currently in the "open" state.
   * Use this to control visibility and trigger CSS transitions.
   */
  isOpen: boolean;

  /**
   * The current value being displayed.
   * This persists during the close animation, allowing content to
   * remain visible while the exit transition plays.
   * Returns `null` when no value has been set or after the delay clears it.
   */
  value: T | null;

  /**
   * Opens the panel with a specific value.
   * Cancels any pending close timeout to prevent race conditions
   * when rapidly opening/closing.
   * @param value - The value to display in the panel
   */
  open: (value: T) => void;

  /**
   * Closes the panel and schedules the value to be cleared after the delay.
   * The value remains available during the delay period for exit animations.
   */
  close: () => void;

  /**
   * Handler for controlled open state changes.
   * Useful for integrating with KUI Sheet or similar components that
   * use an `onOpenChange` callback pattern.
   * @param open - Whether the panel should be open
   */
  onOpenChange: (open: boolean) => void;
}

/**
 * A hook for managing deferred unmounting of panels, modals, or sheets.
 *
 * This hook solves the common problem of content disappearing immediately
 * when closing a panel, before the exit animation can complete. It keeps
 * the value available during a configurable delay period, allowing smooth
 * exit transitions.
 *
 * @template T - The type of value being managed (e.g., a thread ID, item object, etc.)
 * @param options - Configuration options
 * @returns An object containing state and methods for managing the panel
 *
 * @example
 * // Basic usage with a detail panel
 * const { isOpen, value, open, close } = useDeferredUnmount<ThreadItem>();
 *
 * // Open panel with an item
 * <Button onClick={() => open(selectedThread)}>View Details</Button>
 *
 * // Panel renders with persisted value during close animation
 * <Sheet open={isOpen} onOpenChange={(open) => !open && close()}>
 *   {value && <ThreadDetails thread={value} />}
 * </Sheet>
 *
 * @example
 * // Using onOpenChange for controlled components
 * const panel = useDeferredUnmount<string>({ delay: 500 });
 *
 * <Sheet open={panel.isOpen} onOpenChange={panel.onOpenChange}>
 *   <Content id={panel.value} />
 * </Sheet>
 */
export function useDeferredUnmount<T>(
  options: UseDeferredUnmountOptions = {}
): UseDeferredUnmountReturn<T> {
  const { delay = DEFAULT_DELAY } = options;

  // The value to display - persists during close animation
  const [value, setValue] = useState<T | null>(null);
  // Whether the panel should appear open (controls visibility/animation state)
  const [isOpen, setIsOpen] = useState(false);
  // Reference to the cleanup timeout, allowing cancellation on rapid open/close
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Cleanup timeout on component unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  /**
   * Cancels any pending timeout that would clear the value.
   * Called when opening to prevent race conditions.
   */
  const clearPendingTimeout = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  /**
   * Opens the panel with the specified value.
   * Cancels any pending close timeout first to handle rapid interactions.
   */
  const open = useCallback(
    (newValue: T) => {
      clearPendingTimeout();
      setValue(newValue);
      setIsOpen(true);
    },
    [clearPendingTimeout]
  );

  /**
   * Closes the panel and schedules value cleanup after the delay.
   * The value remains available during the delay for exit animations.
   */
  const close = useCallback(() => {
    setIsOpen(false);
    timeoutRef.current = setTimeout(() => {
      setValue(null);
      timeoutRef.current = null;
    }, delay);
  }, [delay]);

  /**
   * Handles open state changes from controlled components.
   * Maps the boolean open state to the appropriate open/close action.
   */
  const onOpenChange = useCallback(
    (open: boolean) => {
      if (open) {
        clearPendingTimeout();
        setIsOpen(true);
      } else {
        close();
      }
    },
    [clearPendingTimeout, close]
  );

  return { isOpen, value, open, close, onOpenChange };
}
