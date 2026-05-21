// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  type ModelDeployment,
  ModelDeploymentStatus,
  type ModelEntity,
  type ModelEntitysPage,
} from '@nemo/sdk/generated/platform/schema';
import type { Meta, StoryObj } from '@storybook/react';
import { CustomModelsDataView } from '@studio/components/dataViews/CustomModelsDataView';
import {
  emptyModelEntitysPage,
  entityStoreCustomizedModel1,
  entityStorePromptTunedModel1,
} from '@studio/mocks/entity-store/models';
import { http, HttpResponse } from 'msw';

const MODELS_API = '/apis/models/v2/workspaces/:workspace/models';
const DEPLOYMENT_API = '/apis/models/v2/workspaces/:workspace/deployments/:name';

const moreCustomModels: ModelEntity[] = [
  {
    id: 'model-custom-2',
    name: 'llama-3.1-8b-instruct-sft-lora',
    workspace: 'default',
    created_at: '2025-02-10T09:15:32.123456',
    updated_at: '2025-02-10T10:45:12.654321',
    base_model: 'meta/llama-3.1-8b-instruct',
    adapters: [
      {
        name: 'lora-adapter',
        fileset: 'default/lora-fileset-2',
        finetuning_type: 'lora',
        workspace: 'default',
      },
    ],
    custom_fields: {},
  },
  {
    id: 'model-custom-3',
    name: 'qwen-2.5-72b-instruct-dpo-qlora',
    workspace: 'default',
    created_at: '2025-03-01T14:22:08.987654',
    updated_at: '2025-03-01T16:30:44.123456',
    base_model: 'qwen/qwen-2.5-72b-instruct',
    adapters: [
      {
        name: 'qlora-adapter',
        fileset: 'default/qlora-fileset',
        finetuning_type: 'qlora',
        workspace: 'default',
      },
    ],
    custom_fields: {},
  },
  {
    id: 'model-custom-4',
    name: 'mistral-7b-v0.3-grpo-all-weights',
    workspace: 'default',
    created_at: '2025-03-05T11:00:00.000000',
    updated_at: '2025-03-05T13:22:18.555555',
    base_model: 'mistralai/mistral-7b-instruct-v0.3',
    finetuning_type: 'all_weights',
    custom_fields: {},
  },
  {
    id: 'model-custom-5',
    name: 'nemotron-4-340b-distillation',
    workspace: 'default',
    created_at: '2025-04-12T08:30:00.000000',
    updated_at: '2025-04-12T12:15:33.111111',
    base_model: 'nvidia/nemotron-4-340b-instruct',
    finetuning_type: 'lora_merged',
    custom_fields: {},
  },
  {
    id: 'model-custom-6',
    name: 'llama-3.2-1b-sft-prompt-tuned',
    workspace: 'default',
    created_at: '2025-05-20T17:45:00.000000',
    updated_at: '2025-05-20T18:10:22.333333',
    base_model: 'meta/llama-3.2-1b-instruct',
    prompt: {
      system_prompt: 'You are a helpful coding assistant.',
    },
    custom_fields: {},
  },
  {
    id: 'model-custom-7',
    name: 'codellama-70b-dataset-XyZ123-dora',
    workspace: 'default',
    created_at: '2025-06-01T22:00:00.000000',
    updated_at: '2025-06-02T03:45:10.777777',
    base_model: 'default/codellama-70b',
    adapters: [
      {
        name: 'dora-adapter',
        fileset: 'default/dora-fileset',
        finetuning_type: 'dora',
        workspace: 'default',
      },
    ],
    custom_fields: {},
  },
  {
    id: 'model-custom-8',
    name: 'gemma-2-9b-it-lora-customer-support',
    workspace: 'default',
    created_at: '2025-06-15T10:20:00.000000',
    updated_at: '2025-06-15T11:55:44.222222',
    base_model: 'google/gemma-2-9b-it',
    adapters: [
      {
        name: 'lora-adapter',
        fileset: 'default/lora-fileset-3',
        finetuning_type: 'lora',
        workspace: 'default',
      },
    ],
    custom_fields: {},
  },
];

const customModelsPage: ModelEntitysPage = {
  data: [entityStorePromptTunedModel1, entityStoreCustomizedModel1, ...moreCustomModels],
  pagination: {
    page: 1,
    page_size: 10,
    current_page_size: 9,
    total_pages: 1,
    total_results: 9,
  },
};

const makeDeployment = (name: string, status: ModelDeploymentStatus): ModelDeployment => ({
  name,
  workspace: 'default',
  created_at: '2025-06-01T00:00:00.000000',
  updated_at: '2025-06-01T00:00:00.000000',
  entity_version: 1,
  config: `${name}-config`,
  config_version: 1,
  status,
});

const deploymentsByName: Record<string, ModelDeployment> = {
  'some-custom-model': makeDeployment('some-custom-model', ModelDeploymentStatus.READY),
  'codellama-70b-dataset-AnxDxZ6MBzFprTU78BAYP9-lora': makeDeployment(
    'codellama-70b-dataset-AnxDxZ6MBzFprTU78BAYP9-lora',
    ModelDeploymentStatus.READY
  ),
  'llama-3.1-8b-instruct-sft-lora': makeDeployment(
    'llama-3.1-8b-instruct-sft-lora',
    ModelDeploymentStatus.PENDING
  ),
  'qwen-2.5-72b-instruct-dpo-qlora': makeDeployment(
    'qwen-2.5-72b-instruct-dpo-qlora',
    ModelDeploymentStatus.ERROR
  ),
  'mistral-7b-v0.3-grpo-all-weights': makeDeployment(
    'mistral-7b-v0.3-grpo-all-weights',
    ModelDeploymentStatus.READY
  ),
  'nemotron-4-340b-distillation': makeDeployment(
    'nemotron-4-340b-distillation',
    ModelDeploymentStatus.CREATED
  ),
  'codellama-70b-dataset-XyZ123-dora': makeDeployment(
    'codellama-70b-dataset-XyZ123-dora',
    ModelDeploymentStatus.READY
  ),
  'gemma-2-9b-it-lora-customer-support': makeDeployment(
    'gemma-2-9b-it-lora-customer-support',
    ModelDeploymentStatus.DELETING
  ),
};

const meta = {
  component: CustomModelsDataView,
  title: 'DataViews/CustomModelsDataView',
  args: {
    workspace: 'default',
  },
} satisfies Meta<typeof CustomModelsDataView>;

export default meta;
type Story = StoryObj<typeof meta>;

const deploymentHandler = http.get<{ name: string }>(DEPLOYMENT_API, ({ params }) => {
  const deployment = deploymentsByName[params.name];
  if (!deployment) return new HttpResponse(null, { status: 404 });
  return HttpResponse.json(deployment);
});

export const Empty: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get<never, never, ModelEntitysPage>(MODELS_API, () =>
          HttpResponse.json(emptyModelEntitysPage)
        ),
      ],
    },
  },
};

export const WithData: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get<never, never, ModelEntitysPage>(MODELS_API, () =>
          HttpResponse.json(customModelsPage)
        ),
        deploymentHandler,
      ],
    },
  },
};
