// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DropdownEntry } from '@nvidia/foundations-react-core';

export type ToolbarFilter = {
  onRemove: () => void;
} & DropdownEntry;
