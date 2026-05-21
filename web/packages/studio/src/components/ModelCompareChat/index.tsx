// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ModelEntity } from '@nemo/sdk/generated/platform/schema';
import { ModelChatPanel } from '@studio/components/ModelChatPanel';
import type { PanelState, SharedModelEntry } from '@studio/routes/ModelCompareRoute/types';
import { FC, useCallback, useState } from 'react';

interface ModelCompareChatProps {
  /** Route workspace — used only as a fallback for panels without an assigned model. */
  workspace: string;
  availableModels: ModelEntity[];
  isLoadingModels: boolean;
  models: SharedModelEntry[];
  onRemoveModel: (id: number) => void;
  onSetModel: (id: number, modelURN: string | null) => void;
}

export const ModelCompareChat: FC<ModelCompareChatProps> = ({
  workspace,
  availableModels,
  isLoadingModels,
  models,
  onRemoveModel,
  onSetModel,
}) => {
  // Per-panel UI state that's view-local (doesn't cross over to Prompts)
  const [collapsedIds, setCollapsedIds] = useState<Set<number>>(new Set());

  const togglePanel = useCallback((id: number) => {
    setCollapsedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  // Full URN flows through to ModelChatPanel and back untouched — no
  // name-only round-trip, so two workspaces that publish the same model name
  // stay unambiguous end-to-end.
  const panels: PanelState[] = models.map((m) => ({
    id: m.id,
    collapsed: collapsedIds.has(m.id),
    modelURN: m.modelURN,
  }));

  return (
    <div className="flex h-full flex-col">
      <div className="flex min-h-0 flex-1 gap-2 overflow-x-auto px-2 pb-2">
        {panels.map((panel) => (
          <ModelChatPanel
            key={panel.id}
            panel={panel}
            fallbackWorkspace={workspace}
            models={availableModels}
            isLoadingModels={isLoadingModels}
            onToggle={togglePanel}
            onRemove={onRemoveModel}
            onModelChange={onSetModel}
          />
        ))}
      </div>
    </div>
  );
};
