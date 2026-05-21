// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  chatCompletionRequest1,
  chatCompletionRequest2,
  chatCompletionRequest3,
  chatCompletionResponse1,
  chatCompletionResponse2,
  chatCompletionResponse3,
} from '@studio/mocks/chat/chat';
import { entityStoreBaseModel1 } from '@studio/mocks/entity-store/models';
import { workspace1 } from '@studio/mocks/entity-store/projects';

const nullFields = {
  session_id: null,
  trace_id: null,
  client_id: null,
  organization_id: null,
  user_id: null,
  status: null,
  error_message: null,
  chosen_response: null,
  suggested_response: null,
  user_comments: null,
  feedback_categories: null,
  classifier_results: null,
  annotations: null,
  schema_version: '',
  description: null,
  type_prefix: null,
  namespace: null,
  custom_fields: null,
  ownership: null,
};

export const completion1 = {
  ...nullFields,
  id: 'feedback-Qx96YssGZLQnXfu9Z6Njao',
  created_at: '2024-10-09 12:30:30.479423',
  updated_at: '2024-10-09 12:34:50.939552',
  raw_request: chatCompletionRequest1,
  raw_response: chatCompletionResponse1,
  project: workspace1.name || '',
  deployment_config: {
    model: entityStoreBaseModel1.name,
  },
  user_rating: 1,
};

export const completion2 = {
  ...nullFields,
  id: 'feedback-YDHeTXZy31ozKVqsCLPdfB',
  created_at: '2024-10-10 15:30:00.325325',
  updated_at: '2024-10-10 15:45:10.113537',
  raw_request: chatCompletionRequest2,
  raw_response: chatCompletionResponse2,
  project: workspace1.name || '',
  deployment_config: {
    model: entityStoreBaseModel1.name,
  },
  user_rating: 1,
  suggested_response: 'Mock user-provided suggested response',
  feedback_categories: {
    clarity: 1,
  },
};

export const completion3 = {
  ...nullFields,
  id: 'feedback-UL3vD491Vmp4MDWXfdiWTw',
  created_at: '2024-10-11 02:14:05.343225',
  updated_at: '2024-10-11 02:34:30.93830',
  raw_request: chatCompletionRequest3,
  raw_response: chatCompletionResponse3,
  project: workspace1.name || '',
  deployment_config: {
    model: entityStoreBaseModel1.name,
  },
  user_rating: 1,
  suggested_response: 'Mock user-provided suggested response',
  feedback_categories: {
    clarity: 1,
  },
};
