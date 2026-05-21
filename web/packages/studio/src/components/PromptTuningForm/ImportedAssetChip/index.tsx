/*
 * SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
 */
import { Flex, Tag } from '@nvidia/foundations-react-core';
import { X } from 'lucide-react';
import { FC } from 'react';

interface Props {
  onDismiss: () => void;
  title: string;
}
export const ImportedAssetChip: FC<Props> = ({ onDismiss, title }) => {
  return (
    <Flex justify="start" gap="density-md" align="center">
      <Tag onClick={onDismiss}>
        <span className="font-normal italic">Copy of {title}</span>
        <X />
      </Tag>
    </Flex>
  );
};
