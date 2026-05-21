// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useBaseModels } from '@nemo/common/src/api/entity-store/useBaseModels';
import { Button, Flex, SegmentedControl } from '@nvidia/foundations-react-core';
import { ModelCompareChat } from '@studio/components/ModelCompareChat';
import { ModelComparePrompts } from '@studio/components/ModelComparePrompts';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import type { SharedModelEntry } from '@studio/routes/ModelCompareRoute/types';
import { Plus } from 'lucide-react';
import { type FC, useCallback, useRef, useState } from 'react';

type CompareView = 'chat' | 'prompts';

const MAX_MODELS = 4;

export const ModelCompareRoute: FC = () => {
  const workspace = useWorkspaceFromPath();
  const { models: availableModels, isLoading: isLoadingModels } = useBaseModels({ workspace });
  const [activeView, setActiveView] = useState<CompareView>('chat');
  const [promptsReady, setPromptsReady] = useState(false);

  // Shared "which models are we comparing" list — owned here, rendered by both views.
  const [models, setModels] = useState<SharedModelEntry[]>([
    { id: 0, modelURN: null },
    { id: 1, modelURN: null },
  ]);
  // Monotonic id counter — using a ref so rapid calls assign unique ids without
  // depending on a stale closure value, and removed ids are never reused (which
  // would otherwise cause stale per-model state in children).
  const nextIdRef = useRef(2);

  const addModel = useCallback(() => {
    setModels((prev) => {
      if (prev.length >= MAX_MODELS) return prev;
      const id = nextIdRef.current;
      nextIdRef.current = id + 1;
      return [...prev, { id, modelURN: null }];
    });
  }, []);

  const removeModel = useCallback((id: number) => {
    setModels((prev) => prev.filter((m) => m.id !== id));
  }, []);

  const setModelRef = useCallback((id: number, modelURN: string | null) => {
    setModels((prev) => prev.map((m) => (m.id === id ? { ...m, modelURN } : m)));
  }, []);

  const atMaxModels = models.length >= MAX_MODELS;
  const addModelDisabled = atMaxModels || (activeView === 'prompts' && !promptsReady);

  return (
    <div className="flex h-full flex-col">
      <Flex align="center" justify="between" className="shrink-0 px-6 py-3">
        <Flex align="center" gap="density-lg">
          <h1 className="text-lg font-semibold">Compare Models</h1>
          <SegmentedControl
            size="tiny"
            value={activeView}
            onValueChange={(value) => setActiveView(value as CompareView)}
            items={[
              { value: 'chat', children: 'Chat' },
              { value: 'prompts', children: 'Run Prompts' },
            ]}
          />
        </Flex>
        <Button kind="secondary" onClick={addModel} disabled={addModelDisabled}>
          <Plus size={16} />
          Add Model
        </Button>
      </Flex>

      <div className={`min-h-0 flex-1 overflow-hidden ${activeView !== 'chat' ? 'hidden' : ''}`}>
        <ModelCompareChat
          workspace={workspace}
          availableModels={availableModels}
          isLoadingModels={isLoadingModels}
          models={models}
          onRemoveModel={removeModel}
          onSetModel={setModelRef}
        />
      </div>
      <div className={`min-h-0 flex-1 overflow-hidden ${activeView !== 'prompts' ? 'hidden' : ''}`}>
        <ModelComparePrompts
          workspace={workspace}
          availableModels={availableModels}
          isLoadingModels={isLoadingModels}
          models={models}
          onRemoveModel={removeModel}
          onSetModel={setModelRef}
          onReadyChange={setPromptsReady}
        />
      </div>
    </div>
  );
};
