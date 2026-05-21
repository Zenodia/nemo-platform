// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/*
 * Shared vitest setup for React/DOM test-bearing packages.
 * Include this in your vitest setupFiles: ['@nemo/testing/react/setup']
 *
 * https://vitest.dev/config/#setupfiles
 */
import * as matchers from '@testing-library/jest-dom/matchers';
import { cleanup } from '@testing-library/react';

expect.extend(matchers);

/*
 * Browser API mocks for KUI and other component libraries.
 * Vitest 4: constructor mocks must use function/class, not arrow functions.
 */

/**
 * This addresses a bug in testing components (ex. KUI or MUI icons) that use libraries that rely on
 * IntersectionObserver (ex. `external-svg-loader`). Without this, we'll see an error like "TypeError:
 * Cannot read properties of undefined (reading 'observe')".
 */
const IntersectionObserverMock = vi.fn(function IntersectionObserverMock() {
  return {
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  };
});
vi.stubGlobal('IntersectionObserver', IntersectionObserverMock);

/**
 * This is a bug in testing components that use KUI. Without this, we'll see
 * an error like "window.ResizeObserver is not a function".
 */
const ResizeObserverMock = vi.fn(function ResizeObserverMock() {
  return {
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  };
});
vi.stubGlobal('ResizeObserver', ResizeObserverMock);

/**
 * Mock MutationObserver for Ariakit components.
 */
const MutationObserverMock = vi.fn(function MutationObserverMock() {
  return {
    observe: vi.fn(),
    disconnect: vi.fn(),
    takeRecords: vi.fn(() => []),
  };
});
vi.stubGlobal('MutationObserver', MutationObserverMock);

/**
 * Mock additional observer APIs that Ariakit might use.
 */
const PerformanceObserverMock = vi.fn(function PerformanceObserverMock() {
  return {
    observe: vi.fn(),
    disconnect: vi.fn(),
    takeRecords: vi.fn(),
  };
});
vi.stubGlobal('PerformanceObserver', PerformanceObserverMock);

/**
 * Mock localStorage to ensure consistent behavior across all tests.
 * jsdom provides localStorage but some Node.js configurations can interfere with it.
 */
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => {
      store[key] = String(value);
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
    get length() {
      return Object.keys(store).length;
    },
    key: (index: number) => Object.keys(store)[index] ?? null,
  };
})();
vi.stubGlobal('localStorage', localStorageMock);

beforeEach(() => {
  /**
   * This is a bug in testing components that use KUI. Without this, we'll see
   * an error like "window.matchMedia is not a function".
   */
  global.matchMedia = vi.fn().mockImplementation((query) => {
    return {
      matches: false,
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    };
  });

  /**
   * Mock HTMLCanvasElement.prototype.getContext to avoid jsdom error:
   * "Not implemented: HTMLCanvasElement.prototype.getContext (without installing the canvas npm package)"
   */
  HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
    fillRect: vi.fn(),
    clearRect: vi.fn(),
    getImageData: vi.fn(),
    putImageData: vi.fn(),
    createImageData: vi.fn(),
    setTransform: vi.fn(),
    drawImage: vi.fn(),
    save: vi.fn(),
    fillText: vi.fn(),
    restore: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    closePath: vi.fn(),
    stroke: vi.fn(),
    translate: vi.fn(),
    scale: vi.fn(),
    rotate: vi.fn(),
    arc: vi.fn(),
    fill: vi.fn(),
    measureText: vi.fn(() => ({ width: 0 })),
    transform: vi.fn(),
    rect: vi.fn(),
    clip: vi.fn(),
  });

  // Set up pointer capture mocks
  window.HTMLElement.prototype.scrollIntoView = vi.fn();
  window.HTMLElement.prototype.hasPointerCapture = vi.fn().mockReturnValue(false);
  window.HTMLElement.prototype.releasePointerCapture = vi.fn();
  window.HTMLElement.prototype.setPointerCapture = vi.fn();
});

afterEach(() => {
  // Unmount all React trees that were mounted with render.
  cleanup();
  // Reset localStorage mock to prevent cross-test state pollution.
  localStorageMock.clear();
  // Clear all timers to prevent timeouts from firing after test completion.
  // This prevents "window is not defined" errors when React tries to update state
  // after the test environment has been torn down.
  vi.clearAllTimers();
  // Restore original implementations for spied functions
  vi.restoreAllMocks();
});
