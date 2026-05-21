// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  type AppendMessage,
  type MessageStatus,
  type ThreadMessageLike,
  useExternalStoreRuntime,
} from '@assistant-ui/react';
import { useCallback, useRef, useState } from 'react';

import { getCompletionText, isAbortError, isChatCompletionStream } from './completionUtils';
import { CANCELLED_STATUS, COMPLETE_STATUS, RUNNING_STATUS } from './constants';
import {
  appendMessageToThreadMessage,
  createTextMessage,
  getEditedMessageIndex,
  getMessageText,
  getOpenAIMessages,
} from './messageUtils';
import type { AssistantChatProps } from './types';
import { useChatCompletion } from '../../hooks/useChatCompletion';

type UseAssistantChatRuntimeOptions = Pick<
  AssistantChatProps,
  | 'baseURL'
  | 'disabled'
  | 'initialMessages'
  | 'model'
  | 'onError'
  | 'promptData'
  | 'tools'
  | 'workspace'
>;

export const useAssistantChatRuntime = ({
  model,
  workspace,
  baseURL,
  promptData,
  tools,
  disabled = false,
  initialMessages = [],
  onError,
}: UseAssistantChatRuntimeOptions) => {
  const [messages, setMessages] = useState<readonly ThreadMessageLike[]>(initialMessages);
  const [isRunning, setIsRunning] = useState(false);
  const messagesRef = useRef<readonly ThreadMessageLike[]>(initialMessages);
  const abortControllerRef = useRef<AbortController | null>(null);
  const { mutateAsync: createChatCompletion } = useChatCompletion();

  const setThreadMessages = useCallback((nextMessages: readonly ThreadMessageLike[]) => {
    messagesRef.current = nextMessages;
    setMessages(nextMessages);
  }, []);

  const updateAssistantMessage = useCallback(
    (assistantMessageId: string, text: string, status: MessageStatus) => {
      setThreadMessages(
        messagesRef.current.map((message) =>
          message.id === assistantMessageId
            ? {
                ...message,
                content: [{ type: 'text', text }],
                status,
              }
            : message
        )
      );
    },
    [setThreadMessages]
  );

  const runCompletion = useCallback(
    async (conversationMessages: readonly ThreadMessageLike[]) => {
      if (disabled) return;

      abortControllerRef.current?.abort();
      const runController = new AbortController();
      abortControllerRef.current = runController;
      const isCurrentRun = () => abortControllerRef.current === runController;

      const assistantMessage = createTextMessage('assistant', '', RUNNING_STATUS);
      setThreadMessages([...conversationMessages, assistantMessage]);
      setIsRunning(true);
      let responseText = '';

      try {
        const result = await createChatCompletion({
          model,
          workspace,
          baseURL,
          messages: getOpenAIMessages(conversationMessages, promptData?.system_prompt),
          max_tokens: promptData?.inference_params?.max_tokens,
          temperature: promptData?.inference_params?.temperature,
          stream: true,
          tools: tools?.length ? tools : undefined,
          signal: runController.signal,
        });

        if (runController.signal.aborted || !isCurrentRun()) {
          updateAssistantMessage(assistantMessage.id!, responseText, CANCELLED_STATUS);
          return;
        }

        if (isChatCompletionStream(result)) {
          const streamController = result.controller;
          runController.signal.addEventListener('abort', () => streamController.abort(), {
            once: true,
          });
          if (runController.signal.aborted) streamController.abort();
          for await (const chunk of result) {
            if (runController.signal.aborted || !isCurrentRun()) break;
            responseText += chunk.choices[0]?.delta.content ?? '';
            updateAssistantMessage(assistantMessage.id!, responseText, RUNNING_STATUS);
          }
          updateAssistantMessage(
            assistantMessage.id!,
            responseText,
            runController.signal.aborted ? CANCELLED_STATUS : COMPLETE_STATUS
          );
        } else {
          updateAssistantMessage(assistantMessage.id!, getCompletionText(result), COMPLETE_STATUS);
        }
      } catch (error: unknown) {
        if (runController.signal.aborted || isAbortError(error)) {
          updateAssistantMessage(assistantMessage.id!, responseText, CANCELLED_STATUS);
          return;
        }

        const errorMessage = error instanceof Error ? error.message : 'Unknown Error';
        const status: MessageStatus = {
          type: 'incomplete',
          reason: 'error',
          error: errorMessage,
        };
        updateAssistantMessage(assistantMessage.id!, errorMessage, status);
        onError?.(error instanceof Error ? error : new Error(errorMessage));
      } finally {
        if (abortControllerRef.current === runController) {
          abortControllerRef.current = null;
          setIsRunning(false);
        }
      }
    },
    [
      baseURL,
      createChatCompletion,
      disabled,
      model,
      onError,
      promptData?.inference_params?.max_tokens,
      promptData?.inference_params?.temperature,
      promptData?.system_prompt,
      setThreadMessages,
      tools,
      updateAssistantMessage,
      workspace,
    ]
  );

  const handleNewMessage = useCallback(
    async (message: AppendMessage) => {
      const text = getMessageText(message).trim();
      if (!text) return;

      const userMessage = appendMessageToThreadMessage({
        ...message,
        content: [{ type: 'text', text }],
      });
      const nextMessages = [...messagesRef.current, userMessage];
      setThreadMessages(nextMessages);
      await runCompletion(nextMessages);
    },
    [runCompletion, setThreadMessages]
  );

  const handleReload = useCallback(async () => {
    const lastAssistantIndex = messagesRef.current.findLastIndex(
      (message) => message.role === 'assistant'
    );
    const nextMessages =
      lastAssistantIndex === -1
        ? messagesRef.current
        : messagesRef.current.slice(0, lastAssistantIndex);

    setThreadMessages(nextMessages);
    await runCompletion(nextMessages);
  }, [runCompletion, setThreadMessages]);

  const handleEdit = useCallback(
    async (message: AppendMessage) => {
      const sourceIndex = getEditedMessageIndex(messagesRef.current, message);
      const previousMessages =
        sourceIndex === -1 ? messagesRef.current : messagesRef.current.slice(0, sourceIndex);
      const text = getMessageText(message).trim();
      if (!text) return;

      const nextMessages = [
        ...previousMessages,
        appendMessageToThreadMessage({
          ...message,
          content: [{ type: 'text', text }],
        }),
      ];
      setThreadMessages(nextMessages);
      await runCompletion(nextMessages);
    },
    [runCompletion, setThreadMessages]
  );

  const handleCancel = useCallback(async () => {
    abortControllerRef.current?.abort();
    setIsRunning(false);
    setThreadMessages(
      messagesRef.current.map((message) =>
        message.role === 'assistant' && message.status?.type === 'running'
          ? { ...message, status: CANCELLED_STATUS }
          : message
      )
    );
  }, [setThreadMessages]);

  const handleReset = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsRunning(false);
    setThreadMessages([]);
  }, [setThreadMessages]);

  const runtime = useExternalStoreRuntime<ThreadMessageLike>({
    messages,
    setMessages: setThreadMessages,
    isDisabled: disabled,
    isRunning,
    onNew: handleNewMessage,
    onEdit: handleEdit,
    onReload: async () => handleReload(),
    onCancel: handleCancel,
    convertMessage: (message) => message,
    unstable_capabilities: {
      copy: true,
    },
  });

  return {
    handleReset,
    runtime,
  };
};
