// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { BreadcrumbsItemProps } from '@studio/providers/breadcrumbs/useBreadcrumbs';
import { Dispatch, SetStateAction } from 'react';

export type SetBreadcrumbsFn = Dispatch<SetStateAction<BreadcrumbsItemProps[]>>;

export interface BreadcrumbsContextValue {
  breadcrumbs: BreadcrumbsItemProps[];
  setBreadcrumbs: SetBreadcrumbsFn;
}
