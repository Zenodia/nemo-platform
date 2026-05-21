// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Stack, Text } from '@nvidia/foundations-react-core';
import type { FC, ReactNode } from 'react';

interface LabeledSectionProps {
  label: string;
  children: ReactNode;
}

/** A small label rendered above content, with breathing room between them.
 *  Used to lay out the per-item reasoning blocks (Question / Expected /
 *  Generated / Score breakdown / Judge reasoning) on the agent-eval detail
 *  page so each labeled chunk reads as a discrete section. */
export const LabeledSection: FC<LabeledSectionProps> = ({ label, children }) => (
  <Stack gap="density-sm">
    <Text kind="label/bold/sm" color="secondary">
      {label}
    </Text>
    {children}
  </Stack>
);
