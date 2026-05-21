// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { AgentConfig } from '@studio/components/dataViews/AgentsDataView';

export const getAgentModelNames = (config: AgentConfig | undefined): string[] => {
  const seen = new Set<string>();
  for (const llm of Object.values(config?.llms ?? {})) {
    if (llm.model_name) seen.add(llm.model_name);
  }
  return [...seen];
};
