// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Loading } from '@studio/components/Layouts/Loading';
import { UnauthorizedWorkspace } from '@studio/components/Layouts/UnauthorizedWorkspace';
import { useAuthTokenStatus } from '@studio/providers/auth/useAuthTokenStatus';
import { useSelectedWorkspace } from '@studio/providers/workspace';
import type { ReactNode } from 'react';

interface WorkspaceGuardProps {
  children: ReactNode;
}

export const WorkspaceGuard = ({ children }: WorkspaceGuardProps) => {
  const { isTokenActive } = useAuthTokenStatus();
  const { selectedWorkspace, isWorkspaceUnauthorized, isWorkspaceLoading } = useSelectedWorkspace();

  if (isTokenActive && selectedWorkspace) {
    if (isWorkspaceLoading) return <Loading description="Checking workspace access..." />;
    if (isWorkspaceUnauthorized) return <UnauthorizedWorkspace />;
  }

  return <>{children}</>;
};
