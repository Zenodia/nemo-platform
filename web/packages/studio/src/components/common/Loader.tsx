// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Spinner, Stack } from '@nvidia/foundations-react-core';
import { FC } from 'react';

/** Compact loading spinner used in forms and inline contexts. */
export const Loader: FC = () => (
  <Stack justify="center" align="center" className="py-4">
    <Spinner data-testid="loader" size="small" description="Loading..." />
  </Stack>
);
