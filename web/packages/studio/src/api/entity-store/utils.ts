// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export const waitForModelSync = async (timeout = 40_000) => {
  await new Promise((resolve) => setTimeout(resolve, timeout));
};
