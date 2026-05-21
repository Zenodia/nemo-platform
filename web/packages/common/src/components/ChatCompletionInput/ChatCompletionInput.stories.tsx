/*
 * SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
 */

import { VariableButton } from '@nemo/common/src/components/buttons/VariableButton';
import {
  ChatCompletionInput,
  defaultChatCompletionMessageRow,
  type ChatCompletionInputProps,
  type ChatCompletionMessageRowValues,
} from '@nemo/common/src/components/ChatCompletionInput';
import type { VariableDef } from '@nemo/common/src/components/form/VariableTextArea';
import { Button, Flex, Stack, Text } from '@nvidia/foundations-react-core';
import type { Meta, StoryObj } from '@storybook/react';
import { FormProvider, useFieldArray, useForm } from 'react-hook-form';

type StoryForm = {
  messages: ChatCompletionMessageRowValues[];
};

type SingleHarnessProps = Partial<Omit<ChatCompletionInputProps<StoryForm>, 'control' | 'name'>> & {
  defaultRow?: ChatCompletionMessageRowValues;
};

function SingleChatCompletionHarness({
  defaultRow,
  disabled,
  footer,
  variables,
  contentPlaceholder,
  roleItems,
  className,
  onMoveUp,
  onMoveDown,
  onDuplicate,
  onRemove,
  allowRemove = true,
}: SingleHarnessProps) {
  const methods = useForm<StoryForm>({
    defaultValues: {
      messages: [defaultRow ?? defaultChatCompletionMessageRow()],
    },
    mode: 'onChange',
  });

  const { fields, append, remove, move, insert } = useFieldArray({
    control: methods.control,
    name: 'messages',
  });

  return (
    <FormProvider {...methods}>
      <Stack gap="density-xl" className="max-w-3xl">
        {fields.map((field, index) => (
          <ChatCompletionInput<StoryForm>
            key={field.id}
            control={methods.control}
            name={`messages.${index}`}
            disabled={disabled}
            footer={footer}
            variables={variables}
            contentPlaceholder={contentPlaceholder}
            roleItems={roleItems}
            className={className}
            onMoveUp={
              onMoveUp ? () => onMoveUp() : index > 0 ? () => move(index, index - 1) : undefined
            }
            onMoveDown={
              onMoveDown
                ? () => onMoveDown()
                : index < fields.length - 1
                  ? () => move(index, index + 1)
                  : undefined
            }
            fieldArrayLength={fields.length}
            onDuplicate={
              onDuplicate
                ? () => onDuplicate()
                : () => {
                    const row = methods.getValues(`messages.${index}`);
                    insert(index + 1, { ...row });
                  }
            }
            onRemove={onRemove ? () => onRemove() : () => remove(index)}
            allowRemove={allowRemove && fields.length > 1}
          />
        ))}
        <Button
          type="button"
          kind="secondary"
          disabled={disabled}
          onClick={() => append(defaultChatCompletionMessageRow())}
        >
          Add Message
        </Button>
      </Stack>
    </FormProvider>
  );
}

function MessageListHarness() {
  const methods = useForm<StoryForm>({
    defaultValues: {
      messages: [
        {
          ...defaultChatCompletionMessageRow(),
          role: 'system',
          content: 'You are a concise assistant.',
          expanded: true,
        },
        {
          ...defaultChatCompletionMessageRow(),
          role: 'user',
          content: 'Summarize the benefits of structured logging.',
          expanded: true,
        },
        {
          ...defaultChatCompletionMessageRow(),
          role: 'assistant',
          content:
            'The benefits of structured logging are that it makes it easier to debug and analyze logs.',
          expanded: true,
        },
      ],
    },
    mode: 'onChange',
  });

  const { fields, append, remove, move, insert } = useFieldArray({
    control: methods.control,
    name: 'messages',
  });

  return (
    <FormProvider {...methods}>
      <Stack gap="density-md" className="max-w-3xl">
        {fields.map((field, index) => (
          <ChatCompletionInput<StoryForm>
            key={field.id}
            control={methods.control}
            name={`messages.${index}`}
            fieldArrayLength={fields.length}
            onMoveUp={index > 0 ? () => move(index, index - 1) : undefined}
            onMoveDown={index < fields.length - 1 ? () => move(index, index + 1) : undefined}
            onDuplicate={() => {
              const row = methods.getValues(`messages.${index}`);
              insert(index + 1, { ...row });
            }}
            onRemove={() => remove(index)}
            allowRemove={fields.length > 1}
          />
        ))}
        <Button
          type="button"
          kind="secondary"
          onClick={() => append(defaultChatCompletionMessageRow())}
        >
          Add Message
        </Button>
      </Stack>
    </FormProvider>
  );
}

const STORY_VARIABLES: VariableDef[] = [
  { name: 'input', description: 'The input from the dataset row.' },
  { name: 'output', description: 'The model output from the dataset row.' },
  { name: 'reference', description: 'The ground-truth reference, if present.' },
];

const meta: Meta<typeof SingleChatCompletionHarness> = {
  component: SingleChatCompletionHarness,
  title: 'Studio Common/ChatCompletionInput',
  decorators: [
    (Story) => (
      <div className="p-density-lg">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<typeof SingleChatCompletionHarness>;

export const Default: Story = {
  name: 'Default (expanded)',
  args: {
    defaultRow: {
      ...defaultChatCompletionMessageRow(),
      content: '',
      expanded: true,
    },
  },
};

export const WithContent: Story = {
  args: {
    defaultRow: {
      ...defaultChatCompletionMessageRow(),
      role: 'assistant',
      content:
        'Here is a multi-line reply.\nIt should autoresize as you type.\nHover the card to see row actions when callbacks are provided.',
      expanded: true,
    },
  },
};

export const Collapsed: Story = {
  args: {
    defaultRow: {
      ...defaultChatCompletionMessageRow(),
      role: 'user',
      content: 'Collapsed rows show a read-only preview; expand to edit.',
      expanded: false,
    },
  },
};

export const WithFooter: Story = {
  args: {
    defaultRow: {
      ...defaultChatCompletionMessageRow(),
      content: 'Footer slot for templates, tools, attachments, etc.',
      expanded: true,
    },
    footer: (
      <Flex align="center" gap="density-sm" className="min-w-0 flex-wrap">
        <Text kind="body/regular/sm" className="text-muted">
          Footer slot
        </Text>
        <Button type="button" kind="tertiary" size="small">
          Insert template
        </Button>
        <Button type="button" kind="tertiary" size="small">
          Add tool
        </Button>
      </Flex>
    ),
  },
};

export const WithRowActions: Story = {
  name: 'Single row with actions (no-op)',
  args: {
    defaultRow: {
      ...defaultChatCompletionMessageRow(),
      content: 'Hover to reveal move / duplicate / delete. Callbacks here are no-ops for demo.',
      expanded: true,
    },
    onMoveUp: () => undefined,
    onMoveDown: () => undefined,
    onDuplicate: () => undefined,
    onRemove: () => undefined,
  },
};

export const DeleteDisabled: Story = {
  name: 'Delete disabled (allowRemove: false)',
  args: {
    defaultRow: {
      ...defaultChatCompletionMessageRow(),
      content: 'Delete control is disabled when allowRemove is false.',
      expanded: true,
    },
    onMoveUp: () => undefined,
    onMoveDown: () => undefined,
    onDuplicate: () => undefined,
    onRemove: () => undefined,
    allowRemove: false,
  },
};

export const Disabled: Story = {
  args: {
    defaultRow: {
      ...defaultChatCompletionMessageRow(),
      role: 'system',
      content: 'This row is disabled.',
      expanded: true,
    },
    disabled: true,
  },
};

export const WithVariables: Story = {
  name: 'With variable highlighting + button',
  args: {
    defaultRow: {
      ...defaultChatCompletionMessageRow(),
      role: 'user',
      content: 'Question: {{input}}\nAnswer:',
      expanded: true,
    },
    variables: STORY_VARIABLES,
    footer: (({ insertVariable }: { insertVariable: (name: string) => void }) => (
      <VariableButton variables={STORY_VARIABLES} onSelect={(v) => insertVariable(v.name)} />
    )) as ChatCompletionInputProps<StoryForm>['footer'],
  },
};

export const MessageList: StoryObj = {
  name: 'Field array (reorder, duplicate, remove)',
  render: () => <MessageListHarness />,
};
