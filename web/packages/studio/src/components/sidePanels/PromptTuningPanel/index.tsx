// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getEntityReference } from '@nemo/common/src/namedEntity';
import { getModelEntityChatStatus } from '@nemo/common/src/utils/models';
import { ModelEntity } from '@nemo/sdk/generated/platform/schema';
import {
  SidePanel,
  Stack,
  TabsContent,
  TabsList,
  TabsRoot,
  TabsTrigger,
  Text,
} from '@nvidia/foundations-react-core';
import { Empty } from '@studio/components/Empty';
import { Loading } from '@studio/components/Layouts/Loading';
import { ModelChat } from '@studio/components/ModelChat';
import { SimpleModelDetailsDisplay } from '@studio/components/sidePanels/PromptTuningPanel/SimpleModelDetailsDisplay';
import {
  DEFAULT_PROMPT_TUNING_FORM_VALUES,
  iclDelimiter,
  modelToFormData,
  PromptTuningFormFields,
} from '@studio/routes/PromptTuningFormRoute/utils';
import { MessagesSquare, Sliders } from 'lucide-react';
import { FormProvider, useForm } from 'react-hook-form';

interface PromptTuningPanelProps {
  model?: ModelEntity;
  workspace: string;
  isLoading?: boolean;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const PromptTuningPanel = ({
  model,
  workspace,
  isLoading = false,
  open,
  onOpenChange,
}: PromptTuningPanelProps) => {
  const values = model ? modelToFormData(model) : DEFAULT_PROMPT_TUNING_FORM_VALUES;

  // Create minimal form context for child components that still need FormProvider
  const form = useForm<PromptTuningFormFields>({
    defaultValues: values,
    disabled: true,
  });

  // destructuring values directly from model data
  const { baseModel, systemPrompt, iclFewShotExamples, toolsEnabled, tools } = values;

  const modelName = model?.name ?? baseModel;
  const chatStatus = model ? getModelEntityChatStatus(model) : 'enabled';

  return (
    <SidePanel
      open={open}
      slotHeading={
        <>
          <MessagesSquare />
          <Text
            kind="label/bold/lg"
            className="truncate"
            title={model && getEntityReference(model)}
          >
            {model && getEntityReference(model)}
          </Text>
        </>
      }
      side="right"
      onOpenChange={onOpenChange}
      bordered
      modal
      className="max-w-[600px] w-full"
    >
      <FormProvider {...form}>
        <Stack className="h-full">
          {isLoading ? (
            <Loading />
          ) : (
            <TabsRoot defaultValue="chat" className="h-full flex flex-col">
              <TabsList>
                <TabsTrigger value="chat">
                  <MessagesSquare />
                  Chat Playground
                </TabsTrigger>
                <TabsTrigger value="details">
                  <Sliders />
                  Model Details
                </TabsTrigger>
              </TabsList>

              <TabsContent value="chat" asChild>
                <Stack className="h-full overflow-auto p-0 pt-6">
                  {modelName ? (
                    <ModelChat
                      workspace={workspace}
                      model={modelName}
                      promptData={{
                        system_prompt: systemPrompt,
                        icl_few_shot_examples: iclFewShotExamples
                          ?.map((icl) => icl.content)
                          .join(iclDelimiter),
                      }}
                      tools={toolsEnabled ? tools : undefined}
                      modelChatStatus={chatStatus}
                      disabled={!baseModel || chatStatus !== 'enabled'}
                    />
                  ) : (
                    <Stack className="h-full justify-center" align="center">
                      <Empty
                        icon={<MessagesSquare size="64" />}
                        title="Awaiting Model Selection"
                        description="Select a base model to get started"
                      />
                    </Stack>
                  )}
                </Stack>
              </TabsContent>

              <TabsContent value="details" asChild>
                <Stack className="h-full overflow-auto p-0 pt-6">
                  <SimpleModelDetailsDisplay
                    modelName={values.name}
                    description={values.description}
                    baseModel={values.baseModel}
                    temperature={values.temperature}
                    maxTokens={values.max_tokens}
                    systemPrompt={values.systemPrompt}
                  />
                </Stack>
              </TabsContent>
            </TabsRoot>
          )}
        </Stack>
      </FormProvider>
    </SidePanel>
  );
};
