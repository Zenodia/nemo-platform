// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { TableEmptyState } from '@nemo/common/src/components/TableEmptyState';
import { removeEmptyValues } from '@nemo/common/src/utils/removeEmptyValues';
import { Button, Stack } from '@nvidia/foundations-react-core';
import { SafeSynthesizerJobsFilterState } from '@studio/components/dataViews/SafeSynthesizerJobsDataView/types';
import { DocumentationButton } from '@studio/components/DocumentationButton';
import { LINK_DOCS_PROJECT } from '@studio/constants/links';
import { getNewSafeSynthesizerRoute } from '@studio/routes/utils';
import { Link } from 'react-router-dom';

export const Empty = ({
  filterState,
  workspace,
}: {
  filterState: SafeSynthesizerJobsFilterState;
  workspace: string;
}) => (
  <Stack className="flex-1 overflow-y-auto" align="center" justify="center">
    <TableEmptyState
      header="No Safe Synthesizer Jobs"
      emptyMessage={
        removeEmptyValues(filterState.search) !== undefined
          ? 'No Safe Synthesizer jobs were found with your search query'
          : 'Generate privacy-safe, synthetic versions of sensitive tabular or free text data with mathematical guarantees of privacy for model training.'
      }
      data-testid="no-safe-synthesizer-jobs-container"
      actions={
        <>
          <DocumentationButton href={LINK_DOCS_PROJECT} />
          <Button asChild color="brand">
            <Link to={getNewSafeSynthesizerRoute(workspace)}>Create New Job</Link>
          </Button>
        </>
      }
    />
  </Stack>
);
