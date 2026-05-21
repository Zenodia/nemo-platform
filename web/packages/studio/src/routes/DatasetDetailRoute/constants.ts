// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Canonical tab IDs for the Dataset Detail page.
 *
 * These string values appear as TabsTrigger/TabsContent `value` props and as
 * the `?tab=<id>` URL query value. Add a tab here, reference it everywhere.
 */
export enum DatasetDetailTab {
  Card = 'card',
  Files = 'files',
}

export const DATASET_DETAIL_DEFAULT_TAB = DatasetDetailTab.Card;

export const isDatasetDetailTab = (value: string | undefined): value is DatasetDetailTab =>
  Object.values(DatasetDetailTab).includes(value as DatasetDetailTab);
