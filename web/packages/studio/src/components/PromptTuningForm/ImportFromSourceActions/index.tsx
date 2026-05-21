// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Stack, Button } from '@nvidia/foundations-react-core';
import { ImportedAssetChip } from '@studio/components/PromptTuningForm/ImportedAssetChip';
import { ImportActionsSource } from '@studio/components/PromptTuningForm/utils';

interface Props {
  chipTitle?: string;
  importButtonDisabled?: boolean; // Is the import button(s) disabled
  onButtonClick?: (source: ImportActionsSource) => void;
  onDismiss: () => void;
  actionsToRender?: ImportActionsSource[];
}
/**
 * A ReactHookForm field component that renders a row of actions
 * for managing imports from library
 */
export const ImportFromSourceActions = ({
  chipTitle,
  importButtonDisabled,
  onButtonClick,
  onDismiss,
  actionsToRender = ['library'],
}: Props) => {
  return (
    <Stack direction="row" justify="end" gap="density-sm">
      <div>
        {chipTitle && (
          <>
            <ImportedAssetChip title={chipTitle} onDismiss={onDismiss} />
          </>
        )}
      </div>
      {actionsToRender.map((action) => (
        <Button
          key={action}
          disabled={importButtonDisabled}
          onClick={() => onButtonClick?.(action)}
          size="small"
        >
          {`Import from ${action.charAt(0).toUpperCase() + action.slice(1)}`}
        </Button>
      ))}
    </Stack>
  );
};
