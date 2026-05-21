// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ModelSelectV2, type ModelSelection } from '@nemo/common/src/components/ModelSelectV2';
import { getPartsFromReference } from '@nemo/common/src/namedEntity';
import { groupModelsByWorkspace } from '@nemo/common/src/utils/models';
import type { ModelEntity } from '@nemo/sdk/generated/platform/schema';
import { ModelChat } from '@studio/components/ModelChat';
import type { PanelState } from '@studio/routes/ModelCompareRoute/types';
import { Minimize2, Trash2 } from 'lucide-react';
import { useCallback, useMemo, type FC } from 'react';

interface ModelChatPanelProps {
  panel: PanelState;
  /** Fallback workspace used only if a panel has no model assigned yet. */
  fallbackWorkspace: string;
  models: ModelEntity[];
  isLoadingModels: boolean;
  onToggle: (id: number) => void;
  onRemove: (id: number) => void;
  /** Receives the full URN ("workspace/name"), or null when cleared. */
  onModelChange: (id: number, modelURN: string | null) => void;
}

export const ModelChatPanel: FC<ModelChatPanelProps> = ({
  panel,
  fallbackWorkspace,
  models,
  isLoadingModels,
  onToggle,
  onRemove,
  onModelChange,
}) => {
  const modelGroups = useMemo(() => groupModelsByWorkspace(models, { sort: true }), [models]);
  const selectedModel: ModelSelection | null = panel.modelURN ? { model: panel.modelURN } : null;

  const handleModelChange = useCallback(
    (selection: ModelSelection) => {
      // ModelSelectV2 emits the full URN — pass it through unchanged so we never
      // ambiguously resolve by bare name across workspaces.
      onModelChange(panel.id, selection.model);
    },
    [panel.id, onModelChange]
  );

  // Derive display label + inference identity from the URN so the chat path
  // uses the model's actual workspace, not a route fallback.
  const parts = panel.modelURN ? getPartsFromReference(panel.modelURN) : null;
  const modelName = parts?.name ?? null;
  const modelWorkspace = parts?.workspace || fallbackWorkspace;

  const collapsedLabel = modelName ?? `Panel ${panel.id}`;

  if (panel.collapsed) {
    return (
      <button
        onClick={() => onToggle(panel.id)}
        className="h-full shrink-0 cursor-pointer rounded-lg border border-base bg-surface-raised px-2 py-4 hover:bg-surface-sunken"
        aria-label={`Expand ${collapsedLabel}`}
      >
        <span className="text-sm font-medium [writing-mode:vertical-rl]">{collapsedLabel}</span>
      </button>
    );
  }

  return (
    <div className="relative flex h-full min-w-[300px] flex-1 flex-col rounded-lg border border-base bg-surface-raised">
      <div className="flex shrink-0 items-center gap-2 border-b border-base p-3">
        <div className="flex-1">
          <ModelSelectV2
            value={selectedModel}
            onValueChange={handleModelChange}
            groups={modelGroups}
            loading={isLoadingModels}
            placeholder={isLoadingModels ? 'Loading models...' : 'Select a model...'}
            hideAdapters
            fullWidth
          />
        </div>
        <button
          onClick={() => onToggle(panel.id)}
          className="cursor-pointer rounded border border-base bg-surface-sunken p-1.5 hover:bg-surface-base"
          aria-label={`Collapse panel ${panel.id}`}
        >
          <Minimize2 size={16} />
        </button>
        <button
          onClick={() => onRemove(panel.id)}
          className="cursor-pointer rounded border border-base bg-surface-sunken p-1.5 hover:bg-surface-base"
          aria-label={`Remove panel ${panel.id}`}
        >
          <Trash2 size={16} />
        </button>
      </div>

      <div className="flex min-h-0 flex-1 flex-col px-3 pb-3">
        {modelName ? (
          <ModelChat model={modelName} workspace={modelWorkspace} />
        ) : (
          <div className="flex flex-1 items-center justify-center text-fg-subdued">
            Select a model to start chatting
          </div>
        )}
      </div>
    </div>
  );
};
