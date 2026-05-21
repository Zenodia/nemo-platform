// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { WorkersContextValue } from '@studio/providers/workers/types';
import { createContext, useContext } from 'react';

export const WorkersContext = createContext<WorkersContextValue | null>(null);

export const useWorkers = () => {
  const context = useContext(WorkersContext);
  if (!context) {
    throw new Error('useWorkers must be used within a WorkersProvider');
  }
  return context;
};
