// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useFilesetsInfinite } from '@nemo/common/src/api/entity-store/useDatasets';
import { ControlledCheckbox } from '@nemo/common/src/components/form/ControlledCheckbox';
import {
  ControlledSearchableSelect,
  SelectItemOption,
} from '@nemo/common/src/components/form/ControlledSearchableSelect';
import { ZodFormField } from '@nemo/common/src/components/form/ZodFormField';
import { KVPair } from '@nemo/common/src/components/KVPair';
import { useListEntries } from '@nemo/sdk/generated/platform/api';
import { EntryFilter, EntrysPage } from '@nemo/sdk/generated/platform/schema';
import { Block, Button, Divider, Flex, Select, Stack, Text } from '@nvidia/foundations-react-core';
import { ExpandableMessage } from '@studio/components/ExpandableMessage';
import {
  getExportCriteriaRender,
  getDefaultExportFileName,
  newExportJobFormSchema,
  supportedCriteria,
} from '@studio/components/form/NewExportJobForm/constants';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { getTextWithCount } from '@studio/util/strings';
import { Database, Trash } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import { useDebounce } from 'use-debounce';
import { z } from 'zod';

export const NewExportJobForm = () => {
  const workspace = useWorkspaceFromPath();
  const [addCriteriaVal, setAddCriteriaVal] = useState<string>('');

  const { control, setValue } = useFormContext<z.infer<typeof newExportJobFormSchema>>();
  const exportFileName = useWatch({ control, name: 'export_file_name' });
  const filters = useWatch({ control, name: 'config.filters' });
  const [debouncedFilters] = useDebounce(filters, 300);
  const usedFilters = useMemo(() => (filters ? Object.keys(filters) : []), [filters]);
  const debouncedUsedFilters = useMemo(
    () => (debouncedFilters ? Object.keys(debouncedFilters) : []),
    [debouncedFilters]
  );

  const {
    data: datasetsPages,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useFilesetsInfinite({
    query: {
      sort: '-created_at',
      filter: { purpose: 'dataset' },
      // TODO: Support filtering and search
      // search: searchQuery ? { name: searchQuery } : undefined,
    },
    workspace,
  });
  const {
    data: entriesData,
    isFetching: isFetchingEntries,
    error: entriesError,
  } = useListEntries(
    workspace,
    {
      page_size: 1,
      filter: debouncedFilters,
    },
    { query: { enabled: debouncedUsedFilters.length > 0 } }
  );

  // Flatten all pages into a single array of options
  const datasetOptions: SelectItemOption[] = useMemo(() => {
    const allDatasets = datasetsPages?.pages.flatMap((page) => page.data) ?? [];
    return allDatasets.map((dataset) => ({
      value: dataset.name ?? '',
      label: dataset.name ?? '',
    }));
  }, [datasetsPages]);

  const handleLoadMore = useCallback(async () => {
    if (hasNextPage && !isFetchingNextPage) {
      await fetchNextPage();
    }
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

  /**
   * Export criteria that are not yet added to the form in filters
   */
  const remainingCriteria = useMemo(() => {
    return supportedCriteria
      .filter((filter) => !usedFilters.includes(filter))
      .map((filter) => ({ value: filter, label: filter }));
  }, [usedFilters]);

  return (
    <Stack gap="6" className="overflow-auto">
      <Text kind="body/regular/md">Export entries to a Dataset for evaluation.</Text>
      <ControlledSearchableSelect
        options={datasetOptions}
        onLoadMore={handleLoadMore}
        onChange={(value) => {
          const datasets = datasetsPages?.pages.flatMap((page) => page.data) ?? [];
          const foundDataset = datasets.find((dataset) => dataset.name === value);
          if (foundDataset) {
            setValue(
              'output_file_url',
              `fileset://${foundDataset.workspace}/${foundDataset.name}/${exportFileName || getDefaultExportFileName()}`
            );
          }
        }}
        hasMore={hasNextPage ?? false}
        isLoading={isLoading}
        isLoadingMore={isFetchingNextPage}
        searchPlaceholder="Search datasets..."
        triggerPlaceholder="Select a dataset"
        emptyMessage="No datasets found"
        doneLoadingMessage="All datasets loaded"
        renderValue={(value) =>
          value ? (
            <Flex align="center" gap="2">
              <Database className="flex-none" />
              <Text kind="body/regular/md">{value}</Text>
            </Flex>
          ) : null
        }
        formFieldProps={{ slotLabel: 'Dataset Destination' }}
        useControllerProps={{ name: 'dataset.name', control }}
      />
      <ZodFormField
        schema={newExportJobFormSchema._def.schema.shape.export_file_name}
        useControllerProps={{ name: 'export_file_name', control }}
      />
      <Flex>
        <Block className="flex-1">
          <ZodFormField
            schema={newExportJobFormSchema._def.schema.shape.config.shape.limit}
            useControllerProps={{ name: 'config.limit', control }}
          />
        </Block>
        <Block className="flex-1" />
      </Flex>
      <ControlledCheckbox
        slotLabel="Use annotation rewrites (when available)"
        formFieldProps={{ slotLabel: 'Row Transformation' }}
        useControllerProps={{ name: 'config.format_options.row_transformation', control }}
      />
      <Divider />
      <Text kind="label/bold/lg">Export Criteria</Text>

      {Object.keys(filters ?? {}).map((filter: string) => {
        const value = getExportCriteriaRender({
          filter: filter as keyof EntryFilter,
          formFieldProps: { slotLabel: '' },
          useControllerProps: { name: `config.filters.${filter}`, control },
        });
        return (
          <Flex
            key={filter}
            className="flex-1 [&>div]:flex-1 [&>div]:items-center"
            gap="2"
            align="center"
          >
            <KVPair
              key={filter}
              label={filter}
              value={value}
              attributes={{
                label: {
                  kind: 'label/bold/sm',
                },
                value: {
                  className: 'flex-1',
                },
              }}
            />
            <Button
              type="button"
              kind="tertiary"
              className="flex-none"
              onClick={() => {
                const newFilters = Object.fromEntries(
                  Object.entries(filters ?? {}).filter(([key]) => key !== filter)
                );
                setValue('config.filters', newFilters, { shouldDirty: true });
              }}
            >
              <Trash />
            </Button>
          </Flex>
        );
      })}
      {remainingCriteria.length > 0 ? (
        <KVPair
          label="Add Criteria"
          value={
            <Select
              aria-label="Add Criteria"
              items={remainingCriteria}
              value={addCriteriaVal}
              placeholder="Select additional criteria"
              onValueChange={(value) => {
                setValue('config.filters', {
                  ...filters,
                  [value]: '',
                });
                setAddCriteriaVal('');
              }}
            />
          }
          attributes={{
            label: {
              kind: 'label/bold/sm',
            },
            value: {
              className: 'flex-1',
            },
          }}
        />
      ) : (
        <Text className="text-secondary w-full text-center" kind="body/regular/md">
          No additional criteria
        </Text>
      )}
      <BottomInfo
        isFetchingEntries={isFetchingEntries}
        entriesError={entriesError}
        usedFilters={usedFilters}
        entriesData={entriesData}
      />
    </Stack>
  );
};

const BottomInfo = ({
  isFetchingEntries,
  entriesError,
  usedFilters,
  entriesData,
}: {
  isFetchingEntries: boolean;
  entriesError: Error | null;
  usedFilters: string[];
  entriesData?: EntrysPage;
}) => {
  const errorMessage = entriesError ? `Error fetching entries: ${entriesError.message}` : undefined;
  const message =
    usedFilters.length > 0
      ? `${getTextWithCount('record', entriesData?.pagination?.total_results ?? 0)} matching the filters will be exported`
      : 'Add at least one filter to export records to a dataset.';
  return (
    <ExpandableMessage message={message} errorMessage={errorMessage} loading={isFetchingEntries} />
  );
};
