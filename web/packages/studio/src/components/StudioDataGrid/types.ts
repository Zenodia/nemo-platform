// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Pagination } from '@nvidia/foundations-react-core';
import { ComponentProps } from 'react';

export type PaginationPageProps = Pick<
  ComponentProps<typeof Pagination>,
  'page' | 'pageSize' | 'pageSizeOptions'
>;
