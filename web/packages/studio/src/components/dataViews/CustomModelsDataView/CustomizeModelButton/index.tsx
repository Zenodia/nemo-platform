// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { LoadingButton } from '@nemo/common/src/components/LoadingButton';
import { getURNFromNamedEntityRef } from '@nemo/common/src/namedEntity';
import type { ModelEntity } from '@nemo/sdk/generated/platform/schema';
import { CreateButton } from '@studio/components/common/CreateButton';
import { CustomizeModelModal } from '@studio/components/CustomizeModelModal';
import { useModelCustomizationEligibility } from '@studio/hooks/useModelCustomizationEligibility';
import { useBoolean } from '@studio/util/hooks/useBoolean';
import type { FC } from 'react';

export interface CustomizeModelButtonProps {
  workspace: string;
  /**
   * When provided, the button is shown in the per-model context: label becomes
   * "Customize this Model", a loading spinner is shown while eligibility is
   * being checked, and the button is disabled if neither fine-tuning (fileset)
   * nor prompt-tuning (lora_enabled deployment) is available.
   */
  model?: ModelEntity;
}

export const CustomizeModelButton: FC<CustomizeModelButtonProps> = ({ workspace, model }) => {
  const [isModalOpen, openModal, closeModal] = useBoolean(false);
  const { canFineTune, canPromptTune, canCustomize, isLoading } =
    useModelCustomizationEligibility(model);

  return (
    <>
      {model ? (
        <LoadingButton
          kind="primary"
          size="small"
          className="flex-1"
          height={28}
          onClick={openModal}
          loading={isLoading}
          disabled={!canCustomize}
        >
          Customize this Model
        </LoadingButton>
      ) : (
        <CreateButton onClick={openModal}>Customize a Model</CreateButton>
      )}
      <CustomizeModelModal
        open={isModalOpen}
        onClose={closeModal}
        workspace={workspace}
        canFineTune={model ? canFineTune : undefined}
        canPromptTune={model ? canPromptTune : undefined}
        modelRef={getURNFromNamedEntityRef(model)}
      />
    </>
  );
};
