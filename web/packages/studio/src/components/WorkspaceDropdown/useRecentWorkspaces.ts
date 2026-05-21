// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { WORKSPACE_DROPDOWN_RECENT_LIMIT } from '@studio/components/WorkspaceDropdown/constants';
import { useWorkspaceFromPathIfExists } from '@studio/hooks/useWorkspaceFromPath';
import { useLocalStorage } from '@studio/util/hooks/useLocalStorage';
import { WORKSPACE_DROPDOWN_RECENT_KEY } from '@studio/util/localStorage';
import { useEffect } from 'react';

export const useRecentWorkspaces = () => {
  const [storedWorkspaces = [], setRecentWorkspaces] = useLocalStorage<string[]>(
    WORKSPACE_DROPDOWN_RECENT_KEY,
    []
  );
  const workspace = useWorkspaceFromPathIfExists();

  // Ensure recentWorkspaces is always an array, even if localStorage contains invalid data
  const recentWorkspaces = Array.isArray(storedWorkspaces) ? storedWorkspaces : [];

  const addRecentWorkspace = (name: string) => {
    const existingIndex = recentWorkspaces.findIndex((w) => w === name);

    if (existingIndex !== -1) {
      // Workspace exists, move to front
      setRecentWorkspaces([name, ...recentWorkspaces.filter((w) => w !== name)]);
    } else if (recentWorkspaces.length >= WORKSPACE_DROPDOWN_RECENT_LIMIT) {
      // Add new workspace and remove oldest
      setRecentWorkspaces([
        name,
        ...recentWorkspaces.slice(0, WORKSPACE_DROPDOWN_RECENT_LIMIT - 1),
      ]);
    } else {
      // Add new workspace
      setRecentWorkspaces([name, ...recentWorkspaces]);
    }
  };

  // We should always use the current workspace in the recent workspaces list
  useEffect(() => {
    if (workspace && recentWorkspaces[0] !== workspace) {
      addRecentWorkspace(workspace);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    recentWorkspaces,
    setRecentWorkspaces,
    addRecentWorkspace,
    removeRecentWorkspace: (name: string) => {
      setRecentWorkspaces(recentWorkspaces.filter((w) => w !== name));
    },
  };
};
