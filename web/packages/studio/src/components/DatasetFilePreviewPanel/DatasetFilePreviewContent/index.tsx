// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { CodeEditor } from '@nemo/common/src/components/CodeEditor';
import { ContentType } from '@nemo/common/src/components/CodeEditor/constants';
import { useFilesListFilesetFiles } from '@nemo/sdk/generated/platform/api';
import { Flex, Stack } from '@nvidia/foundations-react-core';
import { useDatasetFileContent } from '@studio/api/datasets/useDatasetFileContent';
import { FileActions } from '@studio/components/DatasetFilePreviewPanel/components/FileActions';
import { FileBreadcrumbs } from '@studio/components/DatasetFilePreviewPanel/components/FileBreadcrumbs';
import type { FileSystemFile } from '@studio/components/FilesTable/utils';
import { inferJsonContentType, isJsonFile } from '@studio/util/files';
import { FolderOpen } from 'lucide-react';
import { useMemo, type FC } from 'react';

export interface DatasetFilePreviewContentProps {
  // Dataset context
  datasetWorkspace: string;
  datasetName: string;
  filePath: string;

  // Navigation callbacks
  onDatasetClick?: () => void;
  onFolderClick?: (folderPath: string) => void;

  // File actions
  onDeleteSuccess?: () => void;
  onRenameSuccess?: (newPath: string) => void;

  // Optional: pre-fetched data (parent already has the file + content)
  file?: FileSystemFile;
  fileContent?: string;
  isLoading?: boolean;
  error?: Error;

  /**
   * When true, the inline header (breadcrumbs + file actions) is suppressed.
   * The host is responsible for rendering equivalent affordances elsewhere
   * (e.g. a SidePanel slotHeading). Defaults to false.
   */
  hideHeader?: boolean;

  /** Whether the host considers this content active for fetching purposes. Defaults to true. */
  enabled?: boolean;
}

/**
 * Content-only variant of the dataset file preview:
 * breadcrumbs + file actions header + read-only file viewer.
 *
 * No panel chrome. Used inline from FilesTab on the dataset detail page,
 * and composed by `DatasetFilePreviewPanel` (the side-panel wrapper).
 */
export const DatasetFilePreviewContent: FC<DatasetFilePreviewContentProps> = ({
  datasetWorkspace,
  datasetName,
  filePath,
  onDatasetClick,
  onFolderClick,
  onDeleteSuccess,
  onRenameSuccess,
  file: externalFile,
  fileContent: externalContent,
  isLoading: externalLoading,
  error: externalError,
  hideHeader = false,
  enabled = true,
}) => {
  const {
    data: internalContent,
    isLoading: internalLoading,
    error: internalError,
  } = useDatasetFileContent({
    workspace: datasetWorkspace,
    name: datasetName,
    path: filePath,
    enabled: !externalContent && enabled,
  });

  const { data: allFilesResponse } = useFilesListFilesetFiles(
    datasetWorkspace,
    datasetName,
    undefined,
    { query: { enabled: !externalFile && enabled } }
  );
  const allFiles = allFilesResponse?.data;

  const fileContent = externalContent ?? internalContent;
  const isLoading = externalLoading ?? internalLoading;
  const error = externalError ?? internalError;
  const file =
    externalFile ?? (allFiles?.find((f) => f.path === filePath) as FileSystemFile | undefined);

  const body = useMemo(() => {
    if (error) {
      return (
        <div className="flex items-center justify-center h-full text-red-600">
          Error loading file: {error.message}
        </div>
      );
    }

    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-full">
          <span>Loading content...</span>
        </div>
      );
    }

    const jsonContentType = inferJsonContentType(filePath);
    const isJson = isJsonFile(jsonContentType);

    return (
      <CodeEditor
        content={fileContent || ''}
        contentType={isJson ? ContentType.JSON : ContentType.TEXT}
        readOnly
        className="h-full min-h-0"
      />
    );
  }, [fileContent, isLoading, error, filePath]);

  if (hideHeader) {
    return body;
  }

  return (
    <Stack gap="density-sm" className="h-full min-h-0">
      <Flex justify="between" align="center" gap="density-sm" className="shrink-0">
        <Flex gap="density-sm" align="center">
          <FolderOpen width={16} height={16} />
          <FileBreadcrumbs
            datasetName={datasetName}
            filePath={filePath}
            onDatasetClick={onDatasetClick}
            onFolderClick={onFolderClick}
          />
        </Flex>
        {file && (
          <FileActions
            file={file}
            datasetWorkspace={datasetWorkspace}
            datasetName={datasetName}
            onDeleteSuccess={onDeleteSuccess}
            onRenameSuccess={onRenameSuccess}
          />
        )}
      </Flex>
      <div className="flex-1 min-h-0">{body}</div>
    </Stack>
  );
};
