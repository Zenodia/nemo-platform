// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { createContext } from 'react';

interface WorkspaceContextValue {
  selectedWorkspace: string | undefined;
  setSelectedWorkspace: (workspace: string) => void;
  isWorkspaceUnauthorized: boolean;
  isWorkspaceLoading: boolean;
}

export const WorkspaceContext = createContext<WorkspaceContextValue | undefined>(undefined);
