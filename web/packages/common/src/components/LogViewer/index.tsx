// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { triggerDownload } from '@nemo/common/src/utils/file';
import { formatLogs } from '@nemo/common/src/utils/logs';
import type { PlatformJobLog } from '@nemo/sdk/generated/platform/schema';
import {
  Block,
  Button,
  CodeSnippet,
  Flex,
  Spinner,
  Tag,
  Text,
} from '@nvidia/foundations-react-core';
import classNames from 'classnames';
import { ArrowUp, Download } from 'lucide-react';
import { FC, useCallback, useEffect, useMemo, useRef, useState } from 'react';

const DEFAULT_ROW_COUNT = 30;

interface LogViewerProps {
  logs: PlatformJobLog[];
  isLoading?: boolean;
  downloadFilename?: string;
  rows?: number;
  emptyMessage?: string;
}

export const LogViewer: FC<LogViewerProps> = ({
  logs,
  isLoading = false,
  downloadFilename,
  rows = DEFAULT_ROW_COUNT,
  emptyMessage = 'No logs available yet',
}) => {
  const codeScrollRef = useRef<HTMLDivElement>(null);
  const [showAllLogs, setShowAllLogs] = useState(false);
  const shouldAutoScrollRef = useRef(true);
  const tailLogs = logs?.slice(-rows) || [];
  const displayedLogs = showAllLogs ? logs : tailLogs;
  const logText = formatLogs(displayedLogs);
  const hasMoreLogs = logs && logs.length > rows;

  const handleDownload = () => {
    if (downloadFilename) {
      triggerDownload(formatLogs(logs), downloadFilename);
    }
  };

  const scrollToBottomNow = useCallback(() => {
    const codeElement = codeScrollRef.current;
    if (codeElement) {
      const maxScrollTop = codeElement.scrollHeight - codeElement.clientHeight;
      codeElement.scrollTop = maxScrollTop;
    }
  }, []);

  const handleLoadMore = () => {
    shouldAutoScrollRef.current = true;
    setShowAllLogs(true);
  };

  const isShowingLogs = useMemo(() => logs.length > 0 && !isLoading, [logs.length, isLoading]);

  // Watch for actual DOM changes (catches CodeSnippet internal rendering)
  useEffect(() => {
    if (!isShowingLogs) return;
    const codeElement = codeScrollRef.current;
    if (!codeElement) return;

    const mutationObserver = new MutationObserver(() => {
      if (shouldAutoScrollRef.current) {
        scrollToBottomNow();
      }
    });

    mutationObserver.observe(codeElement, {
      childList: true,
      subtree: true,
      characterData: true,
    });

    return () => {
      mutationObserver.disconnect();
    };
  }, [scrollToBottomNow, isShowingLogs, showAllLogs]);

  // Track if user scrolls away from bottom
  useEffect(() => {
    if (!isShowingLogs) return;
    const codeElement = codeScrollRef.current;
    if (!codeElement) return;

    const handleScroll = () => {
      const threshold = 50;
      const isAtBottom =
        Math.abs(codeElement.scrollHeight - codeElement.clientHeight - codeElement.scrollTop) <
        threshold;
      shouldAutoScrollRef.current = isAtBottom;
    };

    codeElement.addEventListener('scroll', handleScroll);

    return () => {
      codeElement.removeEventListener('scroll', handleScroll);
    };
  }, [isShowingLogs, showAllLogs]);

  if (isLoading) {
    return <Spinner size="medium" aria-label="Loading..." />;
  }

  if (!logs || logs.length === 0) {
    return <Block className="text-subtle">{emptyMessage}</Block>;
  }

  return (
    <Block className="relative overflow-hidden">
      {!showAllLogs && hasMoreLogs && (
        <Block className="absolute top-6 mt-[2px] left-px right-px z-10 py-5 text-center bg-[linear-gradient(to_bottom,var(--background-color-surface-sunken),transparent)]">
          <Tag color="gray" kind="solid" onClick={handleLoadMore}>
            <ArrowUp />
            Load previous logs
          </Tag>
        </Block>
      )}
      <CodeSnippet
        language="shell"
        value={logText}
        kind="block"
        collapsible={false}
        rows={rows}
        attributes={{
          CodeSnippetCode: {
            ref: codeScrollRef,
            className: classNames({ '!overflow-y-hidden': !showAllLogs }),
          },
        }}
        slotActions={
          <Flex className="w-full" justify="between" wrap="wrap">
            <Text kind="mono/md">
              {displayedLogs.length} {!showAllLogs && hasMoreLogs && `of ${logs.length}`} lines
            </Text>
            {downloadFilename && (
              <Flex gap="density-sm">
                <Button size="tiny" kind="tertiary" onClick={handleDownload}>
                  <Download />
                </Button>
              </Flex>
            )}
          </Flex>
        }
      />
    </Block>
  );
};
