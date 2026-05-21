// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ControlledSwitch } from '@nemo/common/src/components/form/ControlledSwitch';
import {
  AccordionContent,
  AccordionItem,
  AccordionRoot,
  AccordionTrigger,
  Stack,
  Text,
} from '@nvidia/foundations-react-core';
import type { MetricRunSidePanelFormData } from '@studio/components/sidePanels/MetricRunSidePanel/types';
import { type FC } from 'react';
import { useFormContext } from 'react-hook-form';

export const MetricRunExecutionParametersSection: FC = () => {
  const { control } = useFormContext<MetricRunSidePanelFormData>();

  return (
    <AccordionRoot collapsible>
      <AccordionItem value="execution-parameters" className="border-b-0">
        <AccordionTrigger>
          <Text kind="label/bold/md">Show Execution Parameters (Advanced)</Text>
        </AccordionTrigger>
        <AccordionContent>
          <Stack gap="density-md" className="pt-density-md">
            <ControlledSwitch
              useControllerProps={{ control, name: 'ignore_request_failure' }}
              formFieldProps={{
                slotLabel: 'Ignore request failures',
                slotInfo:
                  'When enabled, failed inference requests are recorded as NaN instead of failing the evaluation.',
              }}
              attributes={{ Flex: { justify: 'start' } }}
            />
          </Stack>
        </AccordionContent>
      </AccordionItem>
    </AccordionRoot>
  );
};
