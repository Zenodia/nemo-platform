// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Stack, Text } from '@nvidia/foundations-react-core';
import { ScoreDefinitions } from '@studio/components/evaluation/Jobs/form/ScoreDefinitions';
import type { FC } from 'react';

export const MetricScoreSection: FC = () => (
  <Stack gap="6">
    <Stack gap="2">
      <Text kind="body/bold/lg">Score Definitions</Text>
      <Text kind="body/regular/md" className="text-secondary">
        Definitions of scores that will be extracted from the judge&apos;s output.
      </Text>
    </Stack>
    <ScoreDefinitions />
  </Stack>
);
