// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getURNFromNamedEntityRef } from '@nemo/common/src/namedEntity';
import { resourceRefSchema, type ResourceRef } from '@nemo/common/src/types';
import { formatFinetuningType } from '@nemo/common/src/utils/formatters';
import type { ModelEntity, PlatformJobStatus } from '@nemo/sdk/generated/platform/schema';
import type {
  CustomizationJob,
  CustomizationJobStatusDetails,
  ParallelismParams,
} from '@nemo/sdk/vendored/customizer/schema';
import { Badge } from '@nvidia/foundations-react-core';
import { getTextWithCount } from '@studio/util/strings';
import { Circle /* TODO: replace with a proper icon (was Circle) */, Gpu } from 'lucide-react';
import { ReactNode } from 'react';

export { formatFinetuningType };

export type FileType = 'training' | 'testing' | 'validation';

/** Training/finetuning type for display (API uses training.type and training.peft). */
export const getFormattedTrainingType = (type?: string) => {
  if (type === undefined) {
    return '';
  }
  switch (type) {
    case 'lora': {
      return 'LoRA';
    }
    case 'sft': {
      return 'SFT';
    }
    case 'dpo': {
      return 'DPO';
    }
    case 'distillation': {
      return 'Distillation';
    }
    default: {
      return type;
    }
  }
};

/**
 * Returns the given status formatted in title case. For example, DEPLOYMENT_IN_PROGRESS returns
 * 'Deployment In Progress', optionally with the progress percentage.
 */
export const getFormattedCustomizationStatus = (
  status?: PlatformJobStatus | string,
  progressPercent?: number
) => {
  let statusText = '';

  if (status) {
    statusText = status
      .split('_')
      .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }

  if (progressPercent !== undefined) {
    statusText += ` (${Math.floor(progressPercent)}%)`;
  }

  return statusText;
};

/**
 * Returns the name of the parent model from a given customization job.
 */
export const getBaseModel = (customizationJob?: CustomizationJob) => {
  if (!customizationJob) {
    return '';
  }
  return customizationJob.spec?.model ?? '';
};

/**
 * Returns the name of the dataset from a given customization job.
 */
export const getDatasetName = (customization: CustomizationJob) => {
  // Platform: dataset is always a URI string in spec
  const datasetURI = customization.spec?.dataset;
  if (typeof datasetURI === 'string') {
    return datasetURI;
  }
  return '';
};

/** Log entry in customization job status_details.status_logs */
interface StatusDetails {
  message?: string;
  detail?: string;
}

/**
 * Returns the error message of the first failure log from a customization job's status details.
 */
export const getFailureMessage = (statusDetails: CustomizationJobStatusDetails): string => {
  const logs: StatusDetails[] = (statusDetails.status_logs as StatusDetails[]) || [];
  const hasFailure = logs.find((log) => log.message?.includes('Failed'));
  if (hasFailure) {
    return logs.map((log) => log.detail || '').join('\n');
  }
  return '';
};

export const getProgressLogs = (statusDetails: CustomizationJobStatusDetails): StatusDetails[] => {
  const logs = (statusDetails.status_logs as StatusDetails[]) || [];
  return logs;
};

/**
 * Returns a string that represents the number of epochs completed by the given customization.
 */
export const getCustomizationTrainingProgress = (customization: CustomizationJob) => {
  if (!customization.status_details) {
    return '';
  }

  const { epochs } = customization.spec?.training || {};

  const { epoch, percentage_done: percentageDone } = customization.status_details || {};

  if (epoch == null && percentageDone == null) {
    return '';
  }

  return `${epoch ?? 0}/${epochs ?? '?'} (${Math.floor(Number(percentageDone) || 0)}%)`;
};

export const getCustomizationConfigurationName = (config: ModelEntity | string) => {
  if (!config) {
    return '';
  }
  if (typeof config === 'string') {
    return config;
  }
  if ('name' in config) {
    return config.name || '';
  }
  return '';
};

export const getCustomizationConfigurationURN = (
  customization?: CustomizationJob
): ResourceRef | undefined => {
  const model = customization?.spec?.model;
  if (!customization || !model) {
    return undefined;
  }
  if (typeof model === 'string') {
    const parsed = resourceRefSchema.safeParse(model);
    return parsed.success ? parsed.data : undefined;
  }
  return getURNFromNamedEntityRef(model);
};

// Platform: training.parallelism has num_gpus_per_node, num_nodes, etc.
type TrainingOptionKey =
  | 'num_gpus_per_node'
  | 'num_nodes'
  | 'tensor_parallel_size'
  | 'sequence_parallel';
const keysToUse: TrainingOptionKey[] = [
  'num_gpus_per_node',
  'num_nodes',
  'tensor_parallel_size',
  'sequence_parallel',
];
const keyToMeta: Partial<
  Record<TrainingOptionKey, { icon?: ReactNode; label: (val: string) => string }>
> = {
  num_gpus_per_node: {
    icon: <Gpu />,
    label: (val: string) => getTextWithCount('GPU', parseInt(val)),
  },
  num_nodes: {
    icon: <Circle />,
    label: (val: string) => getTextWithCount('Node', parseInt(val)),
  },
  tensor_parallel_size: {
    icon: <Gpu />,
    label: (val: string) => getTextWithCount('Tensor Parallel', parseInt(val)),
  },
  sequence_parallel: {
    label: (val: string) => `Sequence: ${val}`,
  },
};

/** Accepts spec.training (has optional parallelism). */
export const getTrainingOptionBadges = (
  training: { parallelism?: ParallelismParams } | null | undefined
): ReactNode[] => {
  const p = training?.parallelism;
  if (!p) return [];
  return keysToUse
    .map((key) => {
      const val = p[key as keyof ParallelismParams]?.toString() ?? '';
      if (val === '' && key !== 'sequence_parallel') return null;
      const meta = keyToMeta[key];
      return (
        <Badge key={key} color="gray" kind="solid">
          {meta?.icon}
          {meta?.label(val)}
        </Badge>
      );
    })
    .filter(Boolean) as ReactNode[];
};

/**
 * The number of steps completed during training.
 * Used for showing a max x-axis value in the loss line chart.
 */
interface GetCustomizationTrainingStepsParams {
  epochs: number;
  trainingRecords: number;
  batchSize: number;
  hasValidationDataset?: boolean;
}
export const getCustomizationTrainingSteps = ({
  epochs,
  trainingRecords,
  batchSize,
  hasValidationDataset,
}: GetCustomizationTrainingStepsParams): number => {
  if (epochs === 0 || batchSize === 0 || trainingRecords === 0) {
    return 0;
  }
  if (hasValidationDataset) {
    // When both training and validation datasets are used
    return epochs * Math.ceil(trainingRecords / batchSize);
  } else {
    // When only training dataset is used (90% split for training)
    return epochs * Math.ceil(Math.ceil(trainingRecords * 0.9) / batchSize);
  }
};
