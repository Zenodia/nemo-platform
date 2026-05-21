// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { FileContentsWithPath } from '@nemo/common/src/data-store/types';
import type { FilesetFileOutput } from '@nemo/sdk/generated/platform/schema';
import {
  FileSystemNode,
  FileSystemFile,
  flattenFileTree,
  isGitkeepPath,
  mapFileListToFileTree,
  toFileEntry,
  TreeRow,
} from '@studio/components/FilesTable/utils';
import { useCallback, useMemo, useState } from 'react';

export interface SortOrder {
  sortBy: 'name' | 'size';
  order: 'asc' | 'desc';
}

export interface UseFileActionsOptions {
  /** Raw files list from API (for search across all files) */
  filesList: FilesetFileOutput[] | undefined;
  isUploading: boolean;
  isFilesFetching: boolean;
  pendingUploads?: (URL | File | FileContentsWithPath)[];
  pendingFileOid?: string;
}

export interface UseFileActionsResult {
  sortOrder: SortOrder;
  sortFiles: (sortBy: 'name' | 'size') => void;
  searchQuery: string;
  handleSearchQueryChange: (value: string, onClearSelection: () => void) => void;
  rowContents: FileSystemNode[];
  treeRows: TreeRow[];
  expandedFolders: Set<string>;
  toggleFolderExpand: (path: string) => void;
}

/**
 * Manages file table actions: sorting, searching, and row content computation
 * - Sort by name or size with asc/desc order
 * - Search filtering across all files
 * - Includes pending uploads in row contents
 */
export function useFileActions(options: UseFileActionsOptions): UseFileActionsResult {
  const {
    filesList,
    isUploading,
    isFilesFetching,
    pendingUploads,
    pendingFileOid = '------PENDING------',
  } = options;

  const [sortOrder, setSortOrder] = useState<SortOrder>({
    sortBy: 'name',
    order: 'asc',
  });

  const sortFiles = useCallback(
    (sortBy: 'name' | 'size') =>
      setSortOrder((q) => ({
        sortBy: sortBy,
        order: q.sortBy !== sortBy ? 'desc' : q.order === 'desc' ? 'asc' : 'desc',
      })),
    []
  );

  const [searchQuery, setSearchQuery] = useState('');

  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(() => new Set());

  const toggleFolderExpand = useCallback((path: string) => {
    setExpandedFolders((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  const handleSearchQueryChange = useCallback((value: string, onClearSelection: () => void) => {
    onClearSelection();
    setSearchQuery(value);
  }, []);

  const { rowContents, treeRows } = useMemo(() => {
    // When searching, show flat filtered list (no tree)
    if (searchQuery && filesList) {
      const baseRows: FileSystemNode[] = filesList
        .filter((file) => !isGitkeepPath(file.path))
        .filter((file) => file.path.toLowerCase().includes(searchQuery.toLowerCase()))
        .map(
          (file): FileSystemFile => ({
            type: 'file',
            path: file.path,
            size: file.size,
            oid: file.file_ref,
          })
        );

      if ((isUploading || isFilesFetching) && pendingUploads?.length) {
        const pendingFiles: FileSystemFile[] = pendingUploads
          .filter((file): file is File => file instanceof File)
          .map((file) => ({
            type: 'file',
            size: file.size,
            path: file.name,
            oid: pendingFileOid,
          }));
        baseRows.push(...pendingFiles);
      }

      const sorted = [...baseRows].sort((a, b) => {
        if (sortOrder.sortBy === 'name') {
          return sortOrder.order === 'asc'
            ? a.path.localeCompare(b.path)
            : b.path.localeCompare(a.path);
        }
        return sortOrder.order === 'asc' ? a.size - b.size : b.size - a.size;
      });

      return {
        rowContents: sorted,
        treeRows: sorted.map((node) => ({ node, depth: 0 })),
      };
    }

    // Tree view: build from filesList and flatten with expanded state
    const fileEntries = (filesList ?? []).map(toFileEntry);
    if ((isUploading || isFilesFetching) && pendingUploads?.length) {
      const pendingFiles = pendingUploads
        .filter((file): file is File => file instanceof File)
        .map((file) => ({
          path: file.name,
          size: file.size,
          oid: pendingFileOid,
        }));
      fileEntries.push(...pendingFiles);
    }

    const fileTree = mapFileListToFileTree(fileEntries);
    const flattened = flattenFileTree(fileTree, expandedFolders, sortOrder);

    return {
      rowContents: flattened.map((t) => t.node),
      treeRows: flattened,
    };
  }, [
    filesList,
    searchQuery,
    sortOrder,
    isFilesFetching,
    isUploading,
    pendingUploads,
    pendingFileOid,
    expandedFolders,
  ]);

  return {
    sortOrder,
    sortFiles,
    searchQuery,
    handleSearchQueryChange,
    rowContents,
    treeRows,
    expandedFolders,
    toggleFolderExpand,
  };
}
