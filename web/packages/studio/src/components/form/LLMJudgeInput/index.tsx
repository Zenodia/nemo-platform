// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ControlledCombobox } from '@nemo/common/src/components/form/ControlledCombobox';
import { ControlledTextArea } from '@nemo/common/src/components/form/ControlledTextArea';
import { ControlledTextInput } from '@nemo/common/src/components/form/ControlledTextInput';
import { Stack } from '@nvidia/foundations-react-core';
import type { AdvancedEvalSettingsFields } from '@studio/components/form/LLMJudgeInput/constants';
import { FC } from 'react';
import { useFormContext } from 'react-hook-form';

export const LLMJudgeInput: FC = () => {
  const { control } = useFormContext<AdvancedEvalSettingsFields>();

  return (
    <Stack gap="density-md">
      <Stack gap="density-sm">
        <h3>Template Messages</h3>
        <ControlledTextArea
          useControllerProps={{ name: 'llmJudgeConfig.template.messages.0.content', control }}
          label="System Message"
        />
        <ControlledTextArea
          useControllerProps={{ name: 'llmJudgeConfig.template.messages.1.content', control }}
          label="User Message"
        />
      </Stack>

      <Stack gap="density-sm">
        <h3>Score Configuration</h3>
        <ControlledCombobox
          useControllerProps={{ name: 'llmJudgeConfig.scores.similarity.type', control }}
          label="Score Type"
          placeholder="int"
          items={['int', 'float']}
        />
        <ControlledTextInput
          useControllerProps={{ name: 'llmJudgeConfig.scores.similarity.parser.pattern', control }}
          label="Parser Pattern"
          placeholder="SIMILARITY: (\\d*)"
          formFieldProps={{
            slotInfo:
              'The pattern to use to parse the score from the LLM response. The first capture group will be used as the score.',
          }}
        />
      </Stack>
    </Stack>
  );
};
