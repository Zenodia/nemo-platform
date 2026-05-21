// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/*
 * KUI mock factory for @nvidia/foundations-react-core.
 *
 * vi.mock is hoisted and statically analyzed per-file, so consumers must call
 * vi.mock in their own setup file. This factory provides the shared implementation.
 *
 * Usage:
 *   import { kuiFoundationsReactMock } from '@nemo/testing/mocks/kui';
 *   vi.mock('@nvidia/foundations-react-core', kuiFoundationsReactMock);
 */
export const kuiFoundationsReactMock = async (importOriginal: () => Promise<unknown>) => {
  const actual = (await importOriginal()) as Record<string, unknown>;
  return {
    ...actual,
    createdBundledHighlighter: () => ({
      codeToHtml: (code: string) => `<span data-mock>${code}</span>`,
      getSingletonHighlighter: () =>
        Promise.resolve({
          codeToHtml: (code: string) => `<span data-mock>${code}</span>`,
          dispose: () => {},
        }),
    }),
    getSingletonHighlighter: () =>
      Promise.resolve({
        codeToHtml: (code: string) => `<span data-mock>${code}</span>`,
        dispose: () => {},
      }),
  };
};
