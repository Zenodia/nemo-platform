// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Stack, Text } from '@nvidia/foundations-react-core';
import type { FC } from 'react';

export interface DatasetCardTabProps {
  workspace: string;
  datasetName: string;
}

export const DatasetCardTab: FC<DatasetCardTabProps> = () => (
  <Stack gap="density-md" data-testid="dataset-card-tab">
    <Text kind="body/regular/md">Dataset Card content lands in a follow-up bead.</Text>
  </Stack>
);
