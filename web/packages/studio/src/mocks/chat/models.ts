// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export const nimModelCard1 = {
  created: 1725579399,
  id: 'meta/codellama-70b',
  object: 'model',
  owned_by: 'system',
  permission: [
    {
      created: 1725579399,
      id: 'modelperm-c8e3c32203d045459cd20e77789fa0ae',
      object: 'model_permission',
      allow_create_engine: false,
      allow_sampling: true,
      allow_logprobs: true,
      allow_search_indices: false,
      allow_view: true,
      allow_fine_tuning: false,
      organization: '*',
      group: null,
      is_blocking: false,
    },
  ],
  root: 'meta/codellama-70b',
  parent: '',
};

export const nimModelCard2 = {
  created: 1725579399,
  id: 'codellama-70b-dataset-AnxDxZ6MBzFprTU78BAYP7-lora',
  object: 'model',
  owned_by: 'system',
  permission: [
    {
      created: 1725579399,
      id: 'modelperm-e84beaafcf85411295925eb965fdcd48',
      object: 'model_permission',
      allow_create_engine: false,
      allow_sampling: true,
      allow_logprobs: true,
      allow_search_indices: false,
      allow_view: true,
      allow_fine_tuning: false,
      organization: '*',
      group: null,
      is_blocking: false,
    },
  ],
  root: 'codellama-70b',
  parent: '',
};

export const getNimLlmModels = () => ({
  data: [nimModelCard1, nimModelCard2],
});
