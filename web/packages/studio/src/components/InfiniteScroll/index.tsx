// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Flex, Spinner } from '@nvidia/foundations-react-core';
import { FC, PropsWithChildren, ReactNode, useCallback, useEffect, useRef, useState } from 'react';

interface Props {
  hasMore: boolean;
  onLoadMore?: () => Promise<void>;
  slotDoneLoading?: ReactNode;
}

export const InfiniteScroll: FC<PropsWithChildren<Props>> = ({
  onLoadMore,
  children,
  hasMore,
  slotDoneLoading,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const loaderRef = useRef(null);

  const loadMoreItems = useCallback(async () => {
    if (isLoading || !hasMore) return;
    setIsLoading(true);
    try {
      if (onLoadMore) {
        await onLoadMore?.();
      }
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, hasMore, setIsLoading, onLoadMore]);

  useEffect(() => {
    let observerRefValue = null;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMoreItems();
        }
      },
      { threshold: 1.0 }
    );

    if (loaderRef.current) {
      observer.observe(loaderRef.current);
      observerRefValue = loaderRef.current;
    }

    return () => {
      if (observerRefValue) {
        observer.unobserve(observerRefValue);
      }
    };
  }, [loaderRef, isLoading, hasMore, loadMoreItems]);

  const doneLoading = slotDoneLoading === undefined ? <div>No data to load</div> : slotDoneLoading;

  return (
    <Flex gap="density-lg" direction="col">
      {children}
      <Flex align="center" justify="center" ref={loaderRef}>
        {isLoading && <Spinner aria-label="Loading" size="small" />}
        {!isLoading && !hasMore && doneLoading}
      </Flex>
    </Flex>
  );
};
