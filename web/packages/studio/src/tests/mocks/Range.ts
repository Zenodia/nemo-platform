// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// Mock Document Range API for text selection and editor components
// Create shared mock objects ONCE and reuse them to avoid memory leaks

// Shared mock DOMRect - created once, reused for all calls
const mockDOMRect: DOMRect = {
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  width: 0,
  height: 0,
  x: 0,
  y: 0,
  toJSON: () => ({}),
};

// Shared mock DOMRectList - created once, reused for all calls
const mockDOMRectList = {
  length: 1,
  item: () => mockDOMRect,
  [Symbol.iterator]: function* () {
    yield mockDOMRect;
  },
  0: mockDOMRect,
} as unknown as DOMRectList;

// Store the original createRange implementation
const originalCreateRange = global.document.createRange.bind(global.document);

// Mock getClientRects on the Range prototype to return the shared mock
global.Range.prototype.getClientRects = vi.fn(() => mockDOMRectList);

// Mock getBoundingClientRect on the Range prototype to return the shared mock
global.Range.prototype.getBoundingClientRect = vi.fn(() => mockDOMRect);

// Keep the original createRange so it returns actual Range instances
global.document.createRange = originalCreateRange;
