// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { AssistantChat, type AssistantChatProps } from '@nemo/common/src/components/AssistantChat';
import type { ModelChatStatus } from '@nemo/common/src/utils/models';
import { handleGenericError } from '@studio/util/logger';
import type { FC } from 'react';

interface ModelChatProps extends Pick<
  AssistantChatProps,
  | 'model'
  | 'workspace'
  | 'baseURL'
  | 'promptData'
  | 'tools'
  | 'assistantName'
  | 'placeholder'
  | 'disabled'
  | 'className'
  | 'initialMessages'
  | 'emptyState'
  | 'onError'
> {
  /**
   * When provided, ModelChat derives default `disabled` state and a
   * status-aware empty state ("Chat Unavailable" / "Model Deployment in
   * Progress") from this status. Explicit `disabled` and `emptyState` take
   * precedence.
   */
  modelChatStatus?: ModelChatStatus;
}

const STATUS_EMPTY_STATE: Record<
  Exclude<ModelChatStatus, 'enabled'>,
  NonNullable<AssistantChatProps['emptyState']>
> = {
  disabled: {
    slotHeading: 'Chat Unavailable',
    slotSubheading: 'This model does not have an active deployment.',
  },
  pending: {
    slotHeading: 'Model Deployment in Progress',
    slotSubheading: 'Check back in a few minutes to chat with this model.',
  },
};

export const ModelChat: FC<ModelChatProps> = ({
  model,
  modelChatStatus,
  disabled,
  assistantName,
  emptyState,
  onError,
  ...rest
}) => {
  const resolvedDisabled = disabled ?? (modelChatStatus ? modelChatStatus !== 'enabled' : false);
  const statusDerivedEmptyState =
    disabled === undefined && modelChatStatus && modelChatStatus !== 'enabled'
      ? STATUS_EMPTY_STATE[modelChatStatus]
      : undefined;
  const resolvedEmptyState = emptyState ?? statusDerivedEmptyState;

  return (
    <AssistantChat
      model={model}
      assistantName={assistantName ?? model}
      disabled={resolvedDisabled}
      emptyState={resolvedEmptyState}
      onError={onError ?? handleGenericError}
      {...rest}
    />
  );
};
