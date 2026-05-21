// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// KUI doesn't export a type that matches the shape MultiSelect's `options`
// prop expects, so we define this custom type.
export interface MultiselectOption {
  value: string;
  label: string;
  isDisabled?: boolean;
}
