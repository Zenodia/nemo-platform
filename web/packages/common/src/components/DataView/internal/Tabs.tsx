// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useInnerDataViewContext } from '@nemo/common/src/components/DataView/internal/context';
import { Tabs as KuiTabs, type TabItem, type TabsProps } from '@nvidia/foundations-react-core';
import { Fragment, useCallback, useMemo, type JSX, type ReactNode } from 'react';

export interface DeprecatedDataViewTab {
  children?: never;
  /**
   * An optional count value to append to the label in parenthesis.
   * @example { label: 'All', count: 10, value: 'all' } => 'All (10)'
   */
  count?: number;
  /**
   * The label to display in the tab. Must be unique.
   * @deprecated Use `children` instead. Will be removed in the next major version.
   */
  label: string;
  /** The value to return when the tab is selected. */
  value: string;
}

/** A DataView Tab. */
export type DataViewTab =
  | DeprecatedDataViewTab
  | (Pick<TabItem, 'children' | 'disabled' | 'attributes' | 'value'> & {
      /** Optional count to append to the label in parenthesis. */
      count?: number;
      /** @deprecated Use `children` instead. */
      label?: never;
    });

/**
 * Renders tabs for the DataView component, used to switch between different views of the data.
 * Should be rendered directly above the table/content.
 */
export function Tabs({
  tabs,
  ...props
}: { tabs: DataViewTab[] } & Partial<TabsProps>): JSX.Element {
  const { state } = useInnerDataViewContext();
  const handleValueChange = useCallback(
    (value: string) => {
      state.tab.set(value);
      state.pagination.goToFirstPage();
    },
    [state.tab, state.pagination]
  );
  const items = useMemo<TabItem[]>(() => {
    return tabs.map((tab) => {
      const tabChildren = (tab.children ?? (tab as DeprecatedDataViewTab).label) as ReactNode;
      const countChildren = tab.count || tab.count === 0 ? ` (${tab.count})` : '';
      if (countChildren) {
        return {
          children: (
            <Fragment>
              {tabChildren}
              {countChildren}
            </Fragment>
          ),
          value: tab.value,
        };
      }
      return { children: tabChildren, value: tab.value };
    });
  }, [tabs]);
  return (
    <KuiTabs
      defaultValue={state.tab.state}
      onValueChange={handleValueChange}
      items={items}
      {...props}
    />
  );
}
