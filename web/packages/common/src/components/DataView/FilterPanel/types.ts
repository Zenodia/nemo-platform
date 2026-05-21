// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { TanstackTable } from '@nemo/common/src/components/DataView/internal';

export type DataViewColumn = TanstackTable.Column<unknown>;

export type MultiState = Record<string, true>;
