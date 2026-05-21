// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useCallback, useState } from 'react';

/**
 * State management hook for DatasetFileManagementSidePanel
 *
 * Provides reusable state management for controlling the sidepanel's
 * open/close state and current folder navigation.
 *
 * @example
 * ```tsx
 * const sidepanel = useDatasetFileManagementState();
 *
 * // Open in specific folder
 * <button onClick={() => sidepanel.openInFolder('training/')}>
 *   View Training Files
 * </button>
 *
 * // Use with Container component
 * <DatasetFileManagementSidePanelContainer
 *   datasetId={datasetId}
 *   open={sidepanel.isOpen}
 *   currentFolder={sidepanel.currentFolder}
 *   onClose={sidepanel.close}
 *   onFolderChange={sidepanel.setFolder}
 * />
 * ```
 */
export interface UseDatasetFileManagementStateResult {
  /** Whether the sidepanel is currently open */
  isOpen: boolean;
  /** Current folder path being viewed in the sidepanel */
  currentFolder?: string;
  /** Opens the sidepanel in a specific folder */
  openInFolder: (folder: string) => void;
  /** Closes the sidepanel */
  close: () => void;
  /** Changes the current folder without closing */
  setFolder: (folder?: string) => void;
}

/**
 * Hook for managing dataset file management sidepanel state
 *
 * This hook provides a clean interface for managing the open/close state
 * and folder navigation of the DatasetFileManagementSidePanel.
 *
 * @returns Object containing state and control methods
 */
export function useDatasetFileManagementState(): UseDatasetFileManagementStateResult {
  const [isOpen, setIsOpen] = useState(false);
  const [currentFolder, setCurrentFolder] = useState<string | undefined>();

  const openInFolder = useCallback((folder: string) => {
    setCurrentFolder(folder);
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  const setFolder = useCallback((folder?: string) => {
    setCurrentFolder(folder);
  }, []);

  return {
    isOpen,
    currentFolder,
    openInFolder,
    close,
    setFolder,
  };
}
