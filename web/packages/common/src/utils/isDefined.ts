// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export const isDefined = <T>(value: T): value is NonNullable<T> => {
  return value !== null && value !== undefined;
};
