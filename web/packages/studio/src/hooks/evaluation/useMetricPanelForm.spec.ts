// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useMetricPanelForm } from '@studio/hooks/evaluation/useMetricPanelForm';
import { renderHook } from '@testing-library/react';

describe('useMetricPanelForm', () => {
  it('does not autoname new metrics', () => {
    const { result } = renderHook(() => useMetricPanelForm());

    expect(result.current.getValues('name')).toBe('');
  });
});
