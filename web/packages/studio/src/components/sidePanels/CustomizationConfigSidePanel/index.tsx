// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { KVPair } from '@nemo/common/src/components/KVPair';
import { useCustomizationGetJob } from '@nemo/sdk/vendored/customizer/api';
import { Divider, Flex, SidePanel, Stack, Text } from '@nvidia/foundations-react-core';
import { ErrorMessageWithRetry } from '@studio/components/ErrorMessageWithRetry';
import { Loading } from '@studio/components/Layouts/Loading';
import {
  getBaseModel,
  getCustomizationConfigurationName,
  getFormattedTrainingType,
  getTrainingOptionBadges,
} from '@studio/util/customizations';
import { ComponentProps, FC } from 'react';

type Props = ComponentProps<typeof SidePanel> & {
  customizationJobName: string;
  workspace?: string;
};
export const CustomizationConfigSidePanel: FC<Props> = ({
  customizationJobName,
  workspace = '',
  ...attributes
}) => {
  const {
    data: job,
    isLoading: isLoadingConfig,
    refetch,
  } = useCustomizationGetJob(workspace, customizationJobName);

  let content;
  if (isLoadingConfig) {
    content = <Loading />;
  } else if (job) {
    const training = job.spec?.training;
    const trainingType = training && 'type' in training ? training.type : undefined;
    const finetuningType = training && 'peft' in training && training.peft ? 'lora' : 'all_weights';
    content = (
      <Stack className="w-full overflow-y-auto" gap="density-xl">
        <KVPair label="Name" value={getCustomizationConfigurationName(job.spec?.model)} />
        <Stack gap="density-sm">
          <Text kind="body/semibold/md">Configuration Snapshot</Text>
          <KVPair label="Base Model" value={getBaseModel(job)} />
          <KVPair label="Training Type" value={getFormattedTrainingType(trainingType)} />
          <KVPair label="Finetuning Type" value={getFormattedTrainingType(finetuningType)} />
          <KVPair
            label="Training Options"
            value={
              training && (
                <Flex gap="density-sm" wrap="wrap" className="w-full">
                  {getTrainingOptionBadges(training)}
                </Flex>
              )
            }
          />
        </Stack>
        <Divider />
        <Stack gap="density-sm">
          <Text kind="body/semibold/md">Hyperparameters</Text>
          <KVPair
            label="Warmup Steps"
            value={training && 'warmup_steps' in training ? training.warmup_steps : undefined}
          />
          <KVPair label="Seed" value={training && 'seed' in training ? training.seed : undefined} />
          <KVPair
            label="Max Steps"
            value={training && 'max_steps' in training ? training.max_steps : undefined}
          />
          <KVPair
            label="Optimizer"
            value={training && 'optimizer' in training ? training.optimizer : undefined}
          />
          <KVPair
            label="Adam Beta 1"
            value={training && 'adam_beta1' in training ? training.adam_beta1 : undefined}
          />
          <KVPair
            label="Adam Beta 2"
            value={training && 'adam_beta2' in training ? training.adam_beta2 : undefined}
          />
          <KVPair
            label="Batch Size"
            value={training && 'batch_size' in training ? training.batch_size : undefined}
          />
          <KVPair
            label="Epochs"
            value={training && 'epochs' in training ? training.epochs : undefined}
          />
          <KVPair
            label="Learning Rate"
            value={training && 'learning_rate' in training ? training.learning_rate : undefined}
          />
          <KVPair
            label="Log Every N Steps"
            value={
              training && 'log_every_n_steps' in training ? training.log_every_n_steps : undefined
            }
          />
          <KVPair
            label="LoRA / Rank"
            value={training && 'peft' in training ? training.peft?.rank : undefined}
          />
          <KVPair
            label="LoRA / Alpha"
            value={training && 'peft' in training ? training.peft?.alpha : undefined}
          />
          <KVPair
            label="LoRA / Target Modules"
            value={
              training && 'peft' in training ? training.peft?.target_modules?.join(', ') : undefined
            }
          />
        </Stack>
      </Stack>
    );
  } else {
    content = (
      <ErrorMessageWithRetry
        onRetry={refetch}
        message="Failed to fetch customization configuration"
      />
    );
  }
  return (
    <SidePanel
      modal
      bordered
      className="w-[440px]"
      {...attributes}
      slotHeading={<Text kind="label/bold/lg">Customization Configuration</Text>}
    >
      {content}
    </SidePanel>
  );
};
