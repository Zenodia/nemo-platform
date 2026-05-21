// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useQueryParams } from '@nemo/common/src/hooks/useQueryParams';
import { getEntityReference } from '@nemo/common/src/namedEntity';
import {
  PageHeader,
  Stack,
  TabsContent,
  TabsList,
  TabsRoot,
  TabsTrigger,
} from '@nvidia/foundations-react-core';
import { AccessibleTitle } from '@studio/components/AccessibleTitle';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { useBreadcrumbs } from '@studio/providers/breadcrumbs/useBreadcrumbs';
import { QUERY_PARAMETERS } from '@studio/routes/constants';
import {
  DATASET_DETAIL_DEFAULT_TAB,
  DatasetDetailTab,
  isDatasetDetailTab,
} from '@studio/routes/DatasetDetailRoute/constants';
import { DatasetCardTab } from '@studio/routes/DatasetDetailRoute/DatasetCardTab';
import { FilesTab } from '@studio/routes/DatasetDetailRoute/FilesTab';
import { getWorkspaceFilesetsRoute } from '@studio/routes/utils';
import { useRequiredPathParams } from '@studio/util/hooks/useRequiredPathParams';
import type { FC } from 'react';

export const DatasetDetailRoute: FC = () => {
  const workspace = useWorkspaceFromPath();
  const { datasetName } = useRequiredPathParams([ROUTE_PARAMS.datasetName]);
  const datasetId = getEntityReference({ namespace: workspace, name: datasetName });

  const { getQueryParam, setQueryParam } = useQueryParams();
  const tabFromUrl = getQueryParam(QUERY_PARAMETERS.tab) || undefined;
  const currentTab: DatasetDetailTab = isDatasetDetailTab(tabFromUrl)
    ? tabFromUrl
    : DATASET_DETAIL_DEFAULT_TAB;

  useBreadcrumbs({
    items: [
      { href: getWorkspaceFilesetsRoute(workspace), slotLabel: 'Filesets' },
      { slotLabel: datasetName },
    ],
  });

  const handleTabChange = (value: string) => {
    if (isDatasetDetailTab(value)) {
      setQueryParam(QUERY_PARAMETERS.tab, value);
    }
  };

  return (
    <AccessibleTitle title={`Dataset ${datasetName}`}>
      <Stack className="w-full h-full min-h-0 p-density-2xl" gap="density-xl">
        <PageHeader slotHeading={datasetName} />
        <TabsRoot
          className="flex-1 min-h-0 flex flex-col"
          value={currentTab}
          onValueChange={handleTabChange}
        >
          <TabsList>
            <TabsTrigger value={DatasetDetailTab.Card}>Dataset Card</TabsTrigger>
            <TabsTrigger value={DatasetDetailTab.Files}>Files</TabsTrigger>
          </TabsList>

          <TabsContent value={DatasetDetailTab.Card} className="p-0">
            <DatasetCardTab workspace={workspace} datasetName={datasetName} />
          </TabsContent>

          <TabsContent value={DatasetDetailTab.Files} className="p-0 flex-1 min-h-0">
            <FilesTab workspace={workspace} datasetName={datasetName} datasetId={datasetId} />
          </TabsContent>
        </TabsRoot>
      </Stack>
    </AccessibleTitle>
  );
};
