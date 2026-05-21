// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { CodeSnippet, Text } from '@nvidia/foundations-react-core';
import type { FC } from 'react';

import { languageInCode } from '../../utils/codeSnippet';

export interface CodeDisplayProps {
  containerClassName?: string;
  children?: string;
}

export const CodeDisplay: FC<CodeDisplayProps> = ({ children, containerClassName }) => {
  const detectedLang = languageInCode(children || '');
  const code = detectedLang ? children?.slice(detectedLang.length).trim() || '' : children || '';

  return (
    <div className={containerClassName || ''} data-testid="code-display">
      <CodeSnippet
        value={code || ''}
        language={detectedLang || 'markdown'}
        kind="block"
        slotActions={
          detectedLang && (
            <Text kind="mono/md" className="w-full">
              {detectedLang}
            </Text>
          )
        }
      />
    </div>
  );
};
