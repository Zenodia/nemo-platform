// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { NamedEntity } from '@nemo/common/src/namedEntity';
import { useDatasetFileContent } from '@studio/api/datasets/useDatasetFileContent';
import { DEFAULT_TOOLS_FILE_NAME } from '@studio/constants/constants';
import { parseFileContent } from '@studio/util/files';
import { ChatCompletionTool } from 'openai/resources/chat/completions.mjs';
import { useMemo } from 'react';

export const useToolsFromDataset = (dataset?: NamedEntity) => {
  const fileContent = useDatasetFileContent({
    workspace: dataset?.workspace ?? dataset?.namespace ?? '',
    name: dataset?.name ?? '',
    enabled: !!dataset,
    path: DEFAULT_TOOLS_FILE_NAME,
    retry: false,
  });

  const parsed = useMemo(
    () =>
      parseFileContent({
        content: fileContent.data || '',
      }),
    [fileContent.data]
  );
  const toolsList = (parsed.rows as unknown as ChatCompletionTool[]).filter(
    (tool) => tool.type === 'function'
  );
  return {
    ...fileContent,
    data: fileContent.data ? toolsList : undefined,
  };
};
