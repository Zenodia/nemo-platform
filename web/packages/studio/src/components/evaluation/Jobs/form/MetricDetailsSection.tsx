// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ControlledTextArea } from '@nemo/common/src/components/form/ControlledTextArea';
import { ControlledTextInput } from '@nemo/common/src/components/form/ControlledTextInput';
import { Stack } from '@nvidia/foundations-react-core';
import type { MetricPanelFormData } from '@studio/hooks/evaluation/useMetricPanelForm';
import { formatWhitespaceHyphens } from '@studio/util/forms/transforms';
import type { FC } from 'react';
import { useFormContext } from 'react-hook-form';

export const MetricDetailsSection: FC = () => {
  const { control, setValue } = useFormContext<MetricPanelFormData>();
  return (
    <Stack gap="2">
      <ControlledTextInput
        useControllerProps={{ control, name: 'name' }}
        label="Metric Name"
        onChange={(e) => {
          setValue('name', formatWhitespaceHyphens(e), {
            shouldValidate: true,
          });
        }}
      />
      <ControlledTextArea
        useControllerProps={{ control, name: 'body.description' }}
        label="Description (optional)"
        resizeable="manual"
      />
    </Stack>
  );
};
