// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Divider, Stack } from '@nvidia/foundations-react-core';
import { MetricDetailsSection } from '@studio/components/evaluation/Jobs/form/MetricDetailsSection';
import { MetricScoreSection } from '@studio/components/evaluation/Jobs/form/MetricScoreSection';
import { MetricTypeSection } from '@studio/components/evaluation/Jobs/form/MetricTypeSection';
import type { FC } from 'react';

export const MetricDetailsPanel: FC = () => (
  <Stack gap="density-2xl">
    <MetricDetailsSection />
    <Divider />
    <MetricTypeSection />
    <Divider />
    <MetricScoreSection />
  </Stack>
);
