// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { VerticalNavItem } from '@nvidia/foundations-react-core';

export type NavInputItem = VerticalNavItem | { group?: string; items: VerticalNavItem[] };

export interface Props {
  items: NavInputItem[];
  bottomItems?: NavInputItem[];
  collapsed?: boolean;
}

export interface NavGroup {
  groupLabel?: string;
  items: VerticalNavItem[];
}
