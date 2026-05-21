// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ThumbDirection } from '@nemo/sdk/generated/platform/schema';
import { Tag } from '@nvidia/foundations-react-core';
import { ThumbsDown, ThumbsUp } from 'lucide-react';
import { FC } from 'react';

export interface ThumbTagProps {
  thumb: ThumbDirection;
}

export const ThumbTag: FC<ThumbTagProps> = ({ thumb }) => {
  return (
    <Tag color={thumb === 'up' ? 'green' : 'red'} readOnly>
      {thumb === 'up' ? (
        <>
          <ThumbsUp size="12" /> Positive
        </>
      ) : (
        <>
          <ThumbsDown size="12" /> Negative
        </>
      )}
    </Tag>
  );
};
