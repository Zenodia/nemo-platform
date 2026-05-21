// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Suppress specific console.warn messages in tests.
 * Non-matching messages pass through to the original console.warn,
 * so failOnConsole still catches unexpected warnings.
 *
 * Cleanup is handled by the global afterEach → vi.restoreAllMocks().
 *
 * @example
 * beforeEach(() => {
 *   suppressConsoleWarn('[DEPRECATED] DatasetsClient');
 * });
 *
 * @example
 * suppressConsoleWarn('first pattern', 'second pattern');
 */
export function suppressConsoleWarn(...patterns: string[]) {
  const original = console.warn.bind(console);
  vi.spyOn(console, 'warn').mockImplementation((...args: unknown[]) => {
    const message = typeof args[0] === 'string' ? args[0] : String(args[0]);
    if (patterns.some((pattern) => message.includes(pattern))) {
      return;
    }
    original(...args);
  });
}

/**
 * Suppress specific console.error messages in tests.
 * Non-matching messages pass through to the original console.error,
 * so failOnConsole still catches unexpected errors.
 *
 * Cleanup is handled by the global afterEach → vi.restoreAllMocks().
 *
 * @example
 * beforeEach(() => {
 *   suppressConsoleError('Error: Uncaught [Error:');
 * });
 */
export function suppressConsoleError(...patterns: string[]) {
  const original = console.error.bind(console);
  vi.spyOn(console, 'error').mockImplementation((...args: unknown[]) => {
    // React 19 calls console.error(errorObject) directly, with component stack
    // appended to error.stack. Check all args and Error stacks for pattern matches.
    const getArgString = (arg: unknown): string => {
      if (arg instanceof Error) {
        return `${arg.toString()}\n${arg.stack ?? ''}`;
      }
      return typeof arg === 'string' ? arg : String(arg);
    };
    const fullMessage = args.map(getArgString).join('\n');
    if (patterns.some((pattern) => fullMessage.includes(pattern))) {
      return;
    }
    original(...args);
  });
}
