// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Accordion } from '@nvidia/foundations-react-core';
import { AdvancedParameters } from '@studio/routes/SafeSynthesizerNewRoute/components/AdvancedParameters';
import { useState } from 'react';

export const AdvancedParametersAccordion = () => {
  const [openAccordion, setOpenAccordion] = useState<string>();
  return (
    <Accordion
      className="[&>div]:border-b-0"
      onValueChange={setOpenAccordion}
      items={[
        {
          slotTrigger: `${openAccordion === 'show-advanced-parameters' ? 'Hide' : 'Show'} Advanced Parameters`,
          slotContent: <AdvancedParameters />,
          value: 'show-advanced-parameters',
        },
      ]}
    />
  );
};
