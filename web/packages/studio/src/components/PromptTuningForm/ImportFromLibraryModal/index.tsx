// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { GridColDef, GridRowSelectionModel, GridSortModel } from '@mui/x-data-grid';
import { Flex, Modal, Button, Block } from '@nvidia/foundations-react-core';
import { Loading } from '@studio/components/Layouts/Loading';
import { StudioDataGrid } from '@studio/components/StudioDataGrid';
import { PaginationPageProps } from '@studio/components/StudioDataGrid/types';
import { UseQueryResult } from '@tanstack/react-query';
import { Dispatch, SetStateAction, useState } from 'react';

const COLUMNS: GridColDef[] = [
  {
    field: 'name',
    headerName: 'Name',
    width: 100,
  },
  {
    field: 'text',
    headerName: 'Text',
    flex: 1,
  },
];

interface WithId {
  id: string;
}

interface Props<T> {
  defaultPaginationModel: PaginationPageProps;
  defaultSortModel: GridSortModel;
  onClickSubmit: (record: T) => void;
  onClose: () => void;
  onPageChange: Dispatch<SetStateAction<PaginationPageProps>>;
  onSortModelChange: Dispatch<SetStateAction<GridSortModel>>;
  open: boolean;
  paginationModel: PaginationPageProps;
  rows?: T[];
  rowCount?: number;
  sortModel: GridSortModel;
  status?: UseQueryResult['status'];
  title: string;
}

export const ImportFromLibraryModal = <T extends WithId>({
  defaultPaginationModel,
  defaultSortModel,
  onClickSubmit,
  onClose,
  onPageChange,
  onSortModelChange,
  open,
  paginationModel,
  rowCount,
  rows,
  sortModel,
  status,
  title,
}: Props<T>) => {
  const [currentRecord, setCurrentRecord] = useState<T>();

  const handleClose = () => {
    // if modal is closed, reset query params to defaults
    setCurrentRecord(undefined);
    onPageChange(defaultPaginationModel);
    onSortModelChange(defaultSortModel);
    onClose();
  };

  const handleRowSelect = (selectedRows: GridRowSelectionModel) => {
    if (rows?.length && selectedRows?.length) {
      const selectedRecord = rows.find((item) => item?.id === selectedRows[0]);
      setCurrentRecord(selectedRecord);
    } else {
      setCurrentRecord(undefined);
    }
  };
  const handleSubmit = () => {
    if (currentRecord) {
      onClickSubmit(currentRecord);
      handleClose();
    }
  };

  const handleSort = (sortModels: GridSortModel) => {
    if (sortModels?.length) {
      // if sorting is active, set it
      onSortModelChange(sortModels);
    } else {
      // if sorting is disabled, reset to default
      onSortModelChange(defaultSortModel);
    }
    // on any sort option change, reset pagination to first page
    onPageChange((prevState) => ({
      ...prevState,
      page: defaultPaginationModel.page,
      pageSize: defaultPaginationModel.pageSize,
    }));
  };

  return (
    <Modal
      open={open}
      onOpenChange={handleClose}
      slotFooter={
        <Flex gap="density-sm" className="w-full justify-end">
          <Button onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={!currentRecord}>
            Apply to Hypermodel
          </Button>
        </Flex>
      }
      slotHeading={title}
      className="overflow-auto flex flex-col min-w-[50vw] min-h-[375px]"
    >
      {status === 'pending' && (
        <Block className="flex-1 flex items-center justify-center">
          <Loading description="Loading assets..." />
        </Block>
      )}
      {status === 'success' && (
        <StudioDataGrid
          checkboxSelection
          columns={COLUMNS}
          disableColumnMenu
          disableMultipleRowSelection
          disableRowSelectionOnClick
          keepNonExistentRowsSelected
          onSortModelChange={handleSort}
          onRowSelectionModelChange={handleRowSelect}
          paginationProps={{
            ...paginationModel,
            totalItems: rowCount ?? 0,
            onPageChange(page: number) {
              onPageChange((prev) => ({
                ...prev,
                page,
              }));
            },
          }}
          paginationMode="server"
          rowCount={rowCount}
          rows={rows}
          sortModel={sortModel}
          sortingMode="server"
        />
      )}
    </Modal>
  );
};
