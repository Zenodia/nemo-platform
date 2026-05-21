// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PaginationQueryState } from '@nemo/common/src/utils/useQueryFromSearchParams';
import { FilesListFilesetsParams } from '@nemo/sdk/generated/platform/schema';

export type DatasetFilterState = PaginationQueryState & {
  filter?: FilesListFilesetsParams['filter'];
};
