// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { VariableDef } from '@nemo/common/src/components/form/VariableTextArea';
import {
  Button,
  DropdownContent,
  DropdownItem,
  DropdownRoot,
  DropdownTrigger,
  Stack,
  Text,
  Tooltip,
} from '@nvidia/foundations-react-core';
import { Plus } from 'lucide-react';
import type { ComponentProps } from 'react';

export interface VariableButtonProps {
  variables: VariableDef[];
  onSelect: (variable: VariableDef) => void;
  disabled?: boolean;
  className?: string;
  attributes?: {
    Button?: ComponentProps<typeof Button>;
    Dropdown?: ComponentProps<typeof DropdownRoot>;
  };
}

export function VariableButton({
  variables,
  onSelect,
  disabled,
  className,
  attributes,
}: VariableButtonProps) {
  const empty = variables.length === 0;
  const isDisabled = Boolean(disabled) || empty;

  const trigger = (
    <Button
      type="button"
      kind="tertiary"
      size="tiny"
      disabled={isDisabled}
      className={className}
      {...attributes?.Button}
    >
      <Plus className="size-3" aria-hidden />
      Variable
    </Button>
  );

  const triggerWithTooltip = empty ? (
    <Tooltip slotContent="No variables available" side="top">
      {trigger}
    </Tooltip>
  ) : (
    trigger
  );

  if (isDisabled) {
    return triggerWithTooltip;
  }

  return (
    <DropdownRoot {...attributes?.Dropdown}>
      <DropdownTrigger asChild showChevron={false}>
        {triggerWithTooltip}
      </DropdownTrigger>
      <DropdownContent align="start">
        {variables.map((v) => (
          <DropdownItem key={v.name} onClick={() => onSelect(v)}>
            <Stack gap="density-xs">
              <Text kind="label/regular/md">{v.name}</Text>
              {v.description ? (
                <Text kind="body/regular/sm" className="text-muted">
                  {v.description}
                </Text>
              ) : null}
            </Stack>
          </DropdownItem>
        ))}
      </DropdownContent>
    </DropdownRoot>
  );
}
