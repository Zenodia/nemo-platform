// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getModelMetadata } from '@nemo/common/src/components/ModelDetailsTooltip/utils';
import { creatorToIcon, tagToIcon } from '@nemo/common/src/constants/modelMetadata';
import { kebabCaseToTitleCase } from '@nemo/common/src/utils/formatters';
import { ModelEntity } from '@nemo/sdk/generated/platform/schema';
import {
  Divider,
  Flex,
  PopoverTriggerProps,
  Stack,
  Tag,
  Text,
  TooltipContent,
  TooltipRoot,
  TooltipTrigger,
} from '@nvidia/foundations-react-core';
import { FC, PropsWithChildren } from 'react';

interface Props {
  triggerProps?: PopoverTriggerProps;
  model: ModelEntity;
}
const MetadataRow = ({ label, value }: { label: string; value: string | undefined }) => {
  if (!value) {
    return null;
  }
  return (
    <Flex>
      <Text className="flex-1 leading-normal">{label}</Text>
      <Text className="flex-1 leading-normal capitalize">{value}</Text>
    </Flex>
  );
};

export const ModelDetailsTooltip: FC<PropsWithChildren<Props>> = ({
  model,
  children,
  triggerProps,
}) => {
  const metadata = getModelMetadata(model);
  if (!metadata) {
    return children;
  }

  return (
    <TooltipRoot openDelayDuration={0}>
      <TooltipContent className="p-0 w-[400px] bg-surface-raised text-primary" side="right">
        <Stack className="w-full">
          <Stack className="p-3" gap="density-lg">
            <Flex gap="density-sm" align="center">
              {creatorToIcon(metadata.creator, { className: 'flex-shrink-0' })}
              <Text fontWeight="bold">{metadata.name.split('@')[0]}</Text>
            </Flex>
            {metadata.description && <Text className="leading-normal">{metadata.description}</Text>}
            {metadata.tags && (
              <Flex gap="density-sm" align="center">
                {metadata.tags?.map((tag) => (
                  <Tag color="gray" kind="outline" key={tag} readOnly>
                    <Flex gap="density-sm" align="center">
                      {tagToIcon(tag)}
                      <Text>{kebabCaseToTitleCase(tag)}</Text>
                    </Flex>
                  </Tag>
                ))}
              </Flex>
            )}
          </Stack>
          <Divider className="bg-interaction-base" />
          <Stack className="p-3" gap="density-md">
            <MetadataRow
              label="Fine-tune Options"
              value={metadata['fine-tune-options']?.join(', ')}
            />
            <MetadataRow label="Creator" value={metadata.creator} />
            <MetadataRow label="Architecture" value={metadata.architecture} />
            <MetadataRow label="Max IO Tokens" value={metadata['max-io-tokens']} />
            <MetadataRow label="Parameters" value={metadata.parameters} />
            <MetadataRow label="Training Data" value={metadata['training-data']} />
            <MetadataRow
              label="Recommended GPUs for Customization"
              value={Object.entries(metadata['recommended-gpus-for-customization'] ?? {})
                .map(([key, value]) => `${key}: ${value}`)
                .join(', ')}
            />
          </Stack>
        </Stack>
      </TooltipContent>
      <TooltipTrigger {...triggerProps}>{children}</TooltipTrigger>
    </TooltipRoot>
  );
};
