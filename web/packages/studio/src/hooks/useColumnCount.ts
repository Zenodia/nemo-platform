// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useCallback, useRef, useState } from 'react';

function getColumnCount(el: HTMLElement): number {
  const cols = getComputedStyle(el).gridTemplateColumns;
  if (!cols || cols === 'none') return 1;
  if (/repeat\(|\(/.test(cols)) {
    return el.querySelectorAll(':scope > *').length || 1;
  }
  return cols.trim().split(/\s+/).length;
}

export function useColumnCount(): [number, (el: HTMLElement | null) => void] {
  const [columnCount, setColumnCount] = useState(1);
  const observerRef = useRef<ResizeObserver | null>(null);

  const setRef = useCallback((el: HTMLElement | null) => {
    observerRef.current?.disconnect();
    observerRef.current = null;
    if (!el) return;

    setColumnCount(getColumnCount(el));
    const observer = new ResizeObserver(() => {
      setColumnCount(getColumnCount(el));
    });
    observer.observe(el);
    observerRef.current = observer;
  }, []);

  return [columnCount, setRef];
}
