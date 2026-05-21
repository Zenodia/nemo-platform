// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { BreadcrumbsContextValue } from '@studio/providers/breadcrumbs/types';
import {
  BreadcrumbsContext,
  BreadcrumbsItemProps,
} from '@studio/providers/breadcrumbs/useBreadcrumbs';
import { FC, PropsWithChildren, useState } from 'react';

export const BreadcrumbsProvider: FC<PropsWithChildren> = ({ children }) => {
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbsItemProps[]>([]);

  const contextValue: BreadcrumbsContextValue = {
    setBreadcrumbs,
    breadcrumbs,
  };

  return <BreadcrumbsContext.Provider value={contextValue}>{children}</BreadcrumbsContext.Provider>;
};
