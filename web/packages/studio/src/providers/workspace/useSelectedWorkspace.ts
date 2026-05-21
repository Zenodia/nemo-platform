// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { WorkspaceContext } from '@studio/providers/workspace/WorkspaceContext';
import { useContext } from 'react';

export const useSelectedWorkspace = () => {
  const context = useContext(WorkspaceContext);

  if (!context) {
    throw new Error('useSelectedWorkspace must be used within a WorkspaceProvider');
  }

  return context;
};
