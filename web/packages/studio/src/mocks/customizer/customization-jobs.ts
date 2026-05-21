// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getURNFromNamedEntityRef } from '@nemo/common/src/namedEntity';
import { CustomizationJob, CustomizationJobsPage } from '@nemo/sdk/vendored/customizer/schema';
import { dataset } from '@studio/mocks/datasets';

export const customizationJob1: CustomizationJob = {
  id: 'cust-4k8XJ8fRYtQT8NTBbjxAqk',
  name: 'meta-llama-3.2-1b-distillation-job',
  created_at: '2025-06-25T21:41:02.067430',
  updated_at: '2025-06-25T21:42:14.242833',
  workspace: 'default',
  project: 'default/project-QRpQtqLB4CJ2fUxKSCWsFX',
  ownership: {
    created_by: '',
    access_policies: {},
  },
  description: 'This is a test customization job',
  spec: {
    dataset: getURNFromNamedEntityRef(dataset)!,
    model: 'meta/llama-3.2-1b-distillation@v1.0.0+A100',
    output: {
      name: 'default/meta-llama-3.2-1b-instruct-dataset-project-QRpQtqLB4CJ2fUxKSCWsFX-all_weights@cust-4k8XJ8fRYtQT8NTBbjxAqk',
      type: 'model',
      fileset: 'default/output-fileset',
    },
    training: {
      type: 'distillation',
      batch_size: 8,
      epochs: 1,
      learning_rate: 0.0001,
      weight_decay: 0.01,
      warmup_steps: 100,
      seed: 42,
      max_steps: 1000,
      optimizer: 'adam_with_flat_lr',
      adam_beta1: 0.9,
      adam_beta2: 0.999,
      log_every_n_steps: 10,
      teacher_model: 'qwen/qwen-2_5-72b-instruct',
      teacher_precision: 'bf16',
      distillation_ratio: 0.5,
      distillation_temperature: 2,
      micro_batch_size: 1,
      sequence_packing: false,
      max_seq_length: 2048,
    },
  },
  status: 'completed',
  status_details: {
    phase: 'completed',
    step: 10,
    max_steps: 10,
    epoch: 1,
    percentage_done: 100,
    backend: 'automodel',
    train_loss: 0.9,
    val_loss: 0.9,
    metrics: {
      train_loss: [
        { value: 0.15, step: 2, epoch: 1 },
        { value: 0.35, step: 4, epoch: 1 },
        { value: 0.55, step: 6, epoch: 1 },
        { value: 0.85, step: 8, epoch: 1 },
        { value: 0.9, step: 10, epoch: 1 },
      ],
      val_loss: [
        { value: 0.5, step: 2, epoch: 1 },
        { value: 0.6, step: 4, epoch: 1 },
        { value: 0.7, step: 6, epoch: 1 },
        { value: 0.8, step: 8, epoch: 1 },
        { value: 0.9, step: 10, epoch: 1 },
      ],
    },
    status_logs: [
      {
        updated_at: '2025-10-24T15:13:17',
        message: 'EntityHandler_0_Created',
      },
      {
        updated_at: '2025-10-24T15:13:17.175399',
        message: 'TrainingJobPending',
        detail: 'The training job is pending',
      },
      {
        updated_at: '2025-10-24T15:13:17.175399',
        message: 'created',
      },
      {
        updated_at: '2025-10-24T15:13:23',
        message: 'EntityHandler_0_Pending',
      },
      {
        updated_at: '2025-10-24T15:13:23',
        message: 'EntityHandler_0_Completed',
      },
      {
        updated_at: '2025-10-24T15:13:23',
        message: 'TrainingJobCreated',
      },
      {
        updated_at: '2025-10-24T15:13:33',
        message: 'TrainingJobRunning',
      },
      {
        updated_at: '2025-10-24T15:16:18',
        message: 'TrainingJobCompleted',
      },
      {
        updated_at: '2025-10-24T15:16:18',
        message: 'EntityHandler_1_Created',
      },
      {
        updated_at: '2025-10-24T15:16:18',
        message: 'EntityHandler_1_Running',
      },
      {
        updated_at: '2025-10-24T15:16:26',
        message: 'EntityHandler_1_Pending',
      },
      {
        updated_at: '2025-10-24T15:16:26',
        message: 'EntityHandler_1_Completed',
      },
    ],
  },
};

export const customizationJob2: CustomizationJob = {
  id: 'cust-DTDYY777TapJkJwkq6jMDD',
  name: 'meta-llama-3.1-8b-sft-lora-job',
  created_at: '2025-06-04T19:10:17.026494',
  updated_at: '2025-06-04T19:15:26.480239',
  workspace: 'default',
  project: 'default/project-QRpQtqLB4CJ2fUxKSCWsFX',
  ownership: {
    created_by: '',
    access_policies: {},
  },
  spec: {
    dataset: getURNFromNamedEntityRef(dataset)!,
    model: 'meta/llama-3.1-8b-instruct@v1.0.0+A100',
    output: {
      name: 'default/meta-llama-3.1-8b-instruct-academic-spoonbill-lora@cust-DTDYY777TapJkJwkq6jMDD',
      type: 'adapter',
      fileset: 'default/output-fileset',
    },
    training: {
      type: 'sft',
      batch_size: 8,
      epochs: 1,
      learning_rate: 0.0001,
      weight_decay: 0.01,
      warmup_steps: 0,
      micro_batch_size: 1,
      sequence_packing: false,
      max_seq_length: 2048,
      max_steps: 1000,
      optimizer: 'adam_with_flat_lr',
      adam_beta1: 0.9,
      adam_beta2: 0.999,
      log_every_n_steps: 10,
      seed: 42,
      peft: {
        type: 'lora',
        rank: 32,
        alpha: 16,
        dropout: 0.1,
        merge: false,
        use_dora: false,
        target_modules: ['q_proj', 'v_proj'],
      },
    },
  },
  status: 'completed',
  status_details: {
    phase: 'completed',
    step: 44,
    max_steps: 44,
    epoch: 1,
    percentage_done: 100,
    backend: 'automodel',
  },
};

export const customizationJob3: CustomizationJob = {
  id: 'cust-7hyykExVYdj9j8wMg6UKe2',
  name: 'meta-llama-3.1-8b-sft-lora-job-long',
  created_at: '2025-06-04T19:10:16.633103',
  updated_at: '2025-06-04T19:34:26.406896',
  workspace: 'default',
  project: 'default/project-QRpQtqLB4CJ2fUxKSCWsFX',
  ownership: {
    created_by: '',
    access_policies: {},
  },
  spec: {
    dataset: getURNFromNamedEntityRef(dataset)!,
    model: 'meta/llama-3.1-8b-instruct@v1.0.0+A100',
    output: {
      name: 'default/meta-llama-3.1-8b-instruct-academic-spoonbill-lora@cust-7hyykExVYdj9j8wMg6UKe2',
      type: 'adapter',
      fileset: 'default/output-fileset',
    },
    training: {
      type: 'sft',
      batch_size: 8,
      epochs: 10,
      learning_rate: 0.0001,
      weight_decay: 0.01,
      warmup_steps: 0,
      micro_batch_size: 1,
      sequence_packing: false,
      max_seq_length: 2048,
      peft: {
        type: 'lora',
        rank: 32,
        alpha: 16,
        dropout: 0.1,
        merge: false,
        use_dora: false,
        target_modules: ['q_proj', 'v_proj'],
      },
    },
  },
  status: 'completed',
  status_details: {
    phase: 'completed',
    step: 440,
    max_steps: 440,
    epoch: 10,
    percentage_done: 100,
    backend: 'automodel',
  },
};

export const customizationJobs: CustomizationJob[] = [
  customizationJob1,
  customizationJob2,
  customizationJob3,
];

export const getCustomizationJobsListResponse: CustomizationJobsPage = {
  data: customizationJobs,
};

export const emptyGetCustomizationJobsResponse: CustomizationJobsPage = {
  data: [],
};
