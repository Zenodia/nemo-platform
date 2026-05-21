// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Utility function to get all current toasts for testing assertions
 */
export const getMockToasts = () => {
  const container = document.querySelector('[data-testid="mock-toast-container"]');
  if (!container) return [];

  return Array.from(container.children).map((toast) => ({
    id: toast.getAttribute('data-toast-id'),
    status: toast.getAttribute('data-testid')?.replace('mock-toast-', ''),
    message: toast.textContent,
    element: toast,
  }));
};

/**
 * Utility function to clear all toasts for clean test state
 */
export const clearMockToasts = () => {
  const container = document.querySelector('[data-testid="mock-toast-container"]');
  if (container) {
    container.innerHTML = '';
  }
};
