// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/*
 * Shared vitest global setup for React/DOM packages.
 * Include in your vitest config: globalSetup: '@n/react/global-setup'
 *
 * https://vitest.dev/config/#globalsetup
 */

export const setup = () => {
  process.env.TZ = 'UTC';
};
