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

import { KVPair } from '@nemo/common/src/components/KVPair';
import { RelativeTime } from '@nemo/common/src/components/RelativeTime';
import type { GuardrailConfig } from '@nemo/sdk/generated/platform/schema';
import { Button, Flex, SidePanel, Stack, Text } from '@nvidia/foundations-react-core';
import { countRails } from '@studio/components/dataViews/GuardrailsDataView/guardrailUtils';
import type { FC } from 'react';

export interface GuardrailsDetailPanelProps {
  open: boolean;
  config: GuardrailConfig;
  onClose: () => void;
  onRequestDelete: (config: GuardrailConfig) => void;
}

export const GuardrailsDetailPanel: FC<GuardrailsDetailPanelProps> = ({
  open,
  config,
  onClose,
  onRequestDelete,
}) => {
  const modelCount = config.data?.models?.length ?? 0;
  const railCount = countRails(config.data);

  return (
    <SidePanel
      className="w-[600px]"
      bordered
      modal
      open={open}
      slotHeading={
        <Text className="min-w-0 truncate" kind="label/bold/lg" title={config.name}>
          {config.name}
        </Text>
      }
      slotFooter={
        <Flex className="w-full" justify="end" gap="density-sm">
          <Button kind="secondary" disabled title="Edit — coming soon">
            Edit
          </Button>
          <Button kind="secondary" color="danger" onClick={() => onRequestDelete(config)}>
            Delete
          </Button>
        </Flex>
      }
      onOpenChange={(nextOpen) => {
        if (!nextOpen) onClose();
      }}
    >
      <Stack className="min-h-0 flex-1 gap-density-lg overflow-auto">
        {/* Details */}
        <Stack className="gap-density-md">
          {config.description ? (
            <KVPair
              label="Description"
              orientation="horizontal"
              size="medium"
              truncate={false}
              value={config.description}
            />
          ) : null}
          <KVPair
            label="Models"
            orientation="horizontal"
            size="medium"
            value={String(modelCount)}
          />
          <KVPair label="Rails" orientation="horizontal" size="medium" value={String(railCount)} />
          <KVPair
            label="Created"
            orientation="horizontal"
            size="medium"
            value={
              config.created_at ? (
                <RelativeTime datetime={config.created_at} focusableForTooltip={false} />
              ) : (
                '—'
              )
            }
          />
          <KVPair
            label="Updated"
            orientation="horizontal"
            size="medium"
            value={
              config.updated_at ? (
                <RelativeTime datetime={config.updated_at} focusableForTooltip={false} />
              ) : (
                '—'
              )
            }
          />
        </Stack>

        {/* Raw config block */}
        {config.data ? (
          <Stack gap="density-sm">
            <Text kind="label/bold/sm">Config</Text>
            <pre className="overflow-auto rounded bg-surface-raised p-density-md text-xs leading-relaxed">
              {JSON.stringify(config.data, null, 2)}
            </pre>
          </Stack>
        ) : null}
      </Stack>
    </SidePanel>
  );
};
