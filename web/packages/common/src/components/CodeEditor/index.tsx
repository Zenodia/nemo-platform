// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { foldGutter } from '@codemirror/language';
import { EditorView, lineNumbers } from '@codemirror/view';
import { BASIC_SETUP, ContentType } from '@nemo/common/src/components/CodeEditor/constants';
import { useExtensionWithDependency } from '@nemo/common/src/components/CodeEditor/extensions/useExtensionWithDependency';
import { useLanguageExtension } from '@nemo/common/src/components/CodeEditor/extensions/useLanguageExtension';
import { useLinter } from '@nemo/common/src/components/CodeEditor/extensions/useLinter';
import { useToast } from '@nemo/common/src/providers/toast/useToast';
import { Flex, Button, useTheme } from '@nvidia/foundations-react-core';
import { githubLight, githubDark } from '@uiw/codemirror-theme-github';
import CodeMirror from '@uiw/react-codemirror';
import { Copy } from 'lucide-react';
import { type FC, type MouseEvent, useState, useMemo, useCallback } from 'react';

import '@nemo/common/src/components/CodeEditor/styles.css';

export interface CodeEditorProps {
  content: string;
  readOnly?: boolean;
  onChange?: (newContent: string) => void;
  contentType?: ContentType;
  hideCopyButton?: boolean;
  hideLineNumbers?: boolean;
  hideFoldGutter?: boolean;
  enableLineWrapping?: boolean;
  hideLinter?: boolean;
  className?: string;
}

export const CodeEditor: FC<CodeEditorProps> = ({
  content,
  readOnly = false,
  contentType = ContentType.JSON,
  onChange,
  className,
  hideCopyButton = false,
  hideLineNumbers = false,
  hideFoldGutter = false,
  enableLineWrapping = true,
  hideLinter = false,
}) => {
  const { theme } = useTheme();
  const toast = useToast();
  const [view, setView] = useState<EditorView | null>(null);

  const handleChange = (newContent: string) => {
    onChange?.(newContent);
  };

  const copyToClipboard = useCallback(
    async (e: MouseEvent<HTMLButtonElement>) => {
      e.preventDefault();
      if (!view) return;
      try {
        const text = view.state.doc.toString();
        await navigator.clipboard.writeText(text);
        toast.success('Copied to clipboard');
      } catch {
        toast.error('Failed to copy to clipboard');
      }
    },
    [toast, view]
  );

  const languageExtension = useLanguageExtension(view, contentType);
  const linterExtension = useLinter(view, contentType, !hideLinter);
  const lineNumbersExtension = useExtensionWithDependency(view, lineNumbers(), !hideLineNumbers);
  const foldGutterExtension = useExtensionWithDependency(view, foldGutter(), !hideFoldGutter);
  const lineWrappingExtension = useExtensionWithDependency(
    view,
    EditorView.lineWrapping,
    enableLineWrapping
  );

  const extensions = useMemo(
    () => [
      languageExtension,
      linterExtension,
      lineNumbersExtension,
      foldGutterExtension,
      lineWrappingExtension,
    ],
    [
      languageExtension,
      linterExtension,
      lineNumbersExtension,
      foldGutterExtension,
      lineWrappingExtension,
    ]
  );

  return (
    <Flex direction="col" gap="density-sm" className={className}>
      {/* Controls inside the editor area */}
      {!hideCopyButton && (
        <Flex justify="end" align="center">
          <Button
            onClick={copyToClipboard}
            kind="tertiary"
            size="tiny"
            aria-label="Copy to clipboard"
          >
            <Copy />
          </Button>
        </Flex>
      )}
      <CodeMirror
        data-testid="nv-code-editor-root"
        value={content}
        basicSetup={BASIC_SETUP}
        height="100%"
        theme={theme === 'dark' ? githubDark : githubLight}
        onCreateEditor={setView}
        extensions={extensions}
        readOnly={readOnly}
        onChange={handleChange}
      />
    </Flex>
  );
};
