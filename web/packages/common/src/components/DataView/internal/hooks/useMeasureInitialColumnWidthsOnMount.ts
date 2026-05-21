// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useInnerDataViewContext } from '@nemo/common/src/components/DataView/internal/context';
import { useIsomorphicLayoutEffect } from '@nemo/common/src/components/DataView/internal/hooks/useIsomorphicLayoutEffect';
import { getHeaderId } from '@nemo/common/src/components/DataView/internal/utils/header-utils';
import { useState } from 'react';

export function useMeasureInitialColumnWidthsOnMount({
  measurementModeRows,
}: {
  measurementModeRows?: number;
}) {
  const { table } = useInnerDataViewContext();
  const [hiddenTable, setHiddenTable] = useState<HTMLTableElement | null>(null);
  const [initialWidths, setInitialWidths] = useState<Record<string, number> | undefined>();

  useIsomorphicLayoutEffect(() => {
    if (hiddenTable && measurementModeRows) {
      const tableHeaderNodes = hiddenTable?.firstChild?.firstChild?.childNodes;
      const widths =
        tableHeaderNodes &&
        Array.from(tableHeaderNodes).map((x) => [
          getHeaderId((x as HTMLElement).id, true),
          (x as HTMLElement).getBoundingClientRect().width,
        ]);
      setInitialWidths(widths ? (Object.fromEntries(widths) as Record<string, number>) : {});
    }
  }, [hiddenTable, measurementModeRows]);

  useIsomorphicLayoutEffect(() => {
    if (initialWidths) {
      table.setColumnSizing(initialWidths);
    }
  }, [initialWidths]);

  return {
    measured: !!initialWidths,
    setMeasurementRef: setHiddenTable,
  };
}
