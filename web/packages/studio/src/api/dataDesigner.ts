// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { customFetch, type ErrorType } from '@nemo/sdk/generated/fetchers/platform';
import type {
  HTTPValidationError,
  PaginationData,
  PlatformJobResultResponse,
  PlatformJobStatus,
} from '@nemo/sdk/generated/platform/schema';
import {
  type QueryClient,
  type UseMutationOptions,
  type UseMutationResult,
  type UseQueryOptions,
  type UseQueryResult,
  useMutation,
  useQuery,
} from '@tanstack/react-query';

type JsonObject = Record<string, unknown>;

export type DataDesignerColumn = {
  name?: string;
  column_type?: string;
  model_alias?: string;
} & JsonObject;

export type DataDesignerModelConfig = {
  alias?: string;
  model?: string;
  provider?: string;
  inference_parameters?: JsonObject;
} & JsonObject;

export type DataDesignerConfig = {
  columns: DataDesignerColumn[];
  model_configs?: DataDesignerModelConfig[];
} & JsonObject;

export interface DataDesignerJobSpec {
  num_records?: number;
  config?: DataDesignerConfig;
  [key: string]: unknown;
}

export interface DataDesignerJobRequest {
  name?: string;
  description?: string;
  project?: string;
  spec?: DataDesignerJobSpec;
  [key: string]: unknown;
}

export interface DataDesignerJob {
  id?: string;
  workspace?: string;
  name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  spec: DataDesignerJobSpec;
  status?: PlatformJobStatus;
  [key: string]: unknown;
}

export type DataDesignerJobsSortField = string;
export type DataDesignerJobsListFilter = Record<string, unknown>;

export type DataDesignerListJobsParams = Record<string, unknown> & {
  page?: number;
  page_size?: number;
  sort?: DataDesignerJobsSortField;
  filter?: DataDesignerJobsListFilter;
};

export interface DataDesignerJobsPage {
  data?: DataDesignerJob[];
  pagination?: PaginationData;
  [key: string]: unknown;
}

export interface DataDesignerJobResultsPage {
  data?: PlatformJobResultResponse[];
}

const dataDesignerJobPath = (workspace: string, path = '') =>
  `/apis/data-designer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs${path}`;

type QueryOptions<TData, TError> = {
  query?: Partial<UseQueryOptions<TData, TError, TData>>;
};

type MutationOptions<TData, TVariables, TError, TContext> = {
  mutation?: UseMutationOptions<TData, TError, TVariables, TContext>;
};

export const dataDesignerCreateJob = (
  workspace: string,
  data: DataDesignerJobRequest,
  signal?: AbortSignal
) =>
  customFetch<DataDesignerJob>({
    url: dataDesignerJobPath(workspace),
    method: 'POST',
    data,
    signal,
  });

export const useDataDesignerCreateJob = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(
  options?: MutationOptions<
    Awaited<ReturnType<typeof dataDesignerCreateJob>>,
    { workspace: string; data: DataDesignerJobRequest },
    TError,
    TContext
  >,
  queryClient?: QueryClient
): UseMutationResult<
  Awaited<ReturnType<typeof dataDesignerCreateJob>>,
  TError,
  { workspace: string; data: DataDesignerJobRequest },
  TContext
> =>
  useMutation(
    {
      mutationKey: ['dataDesignerCreateJob'],
      mutationFn: ({ workspace, data }) => dataDesignerCreateJob(workspace, data),
      ...options?.mutation,
    },
    queryClient
  );

export const dataDesignerListJobs = (
  workspace: string,
  params?: DataDesignerListJobsParams,
  signal?: AbortSignal
) =>
  customFetch<DataDesignerJobsPage>({
    url: dataDesignerJobPath(workspace),
    method: 'GET',
    params,
    signal,
  });

export const getDataDesignerListJobsQueryKey = (
  workspace: string,
  params?: DataDesignerListJobsParams
) => [dataDesignerJobPath(workspace), ...(params ? [params] : [])] as const;

export const useDataDesignerListJobs = <TError = ErrorType<HTTPValidationError>>(
  workspace: string,
  params?: DataDesignerListJobsParams,
  options?: QueryOptions<Awaited<ReturnType<typeof dataDesignerListJobs>>, TError>,
  queryClient?: QueryClient
): UseQueryResult<Awaited<ReturnType<typeof dataDesignerListJobs>>, TError> =>
  useQuery(
    {
      queryKey: getDataDesignerListJobsQueryKey(workspace, params),
      queryFn: ({ signal }) => dataDesignerListJobs(workspace, params, signal),
      enabled: !!workspace,
      ...options?.query,
    },
    queryClient
  );

export const dataDesignerGetJob = (workspace: string, name: string, signal?: AbortSignal) =>
  customFetch<DataDesignerJob>({
    url: dataDesignerJobPath(workspace, `/${encodeURIComponent(String(name))}`),
    method: 'GET',
    signal,
  });

export const getDataDesignerGetJobQueryKey = (workspace: string, name: string) =>
  ['dataDesigner', 'job', workspace, name] as const;

export const useDataDesignerGetJob = <TError = ErrorType<HTTPValidationError>>(
  workspace: string,
  name: string,
  options?: QueryOptions<Awaited<ReturnType<typeof dataDesignerGetJob>>, TError>,
  queryClient?: QueryClient
): UseQueryResult<Awaited<ReturnType<typeof dataDesignerGetJob>>, TError> =>
  useQuery(
    {
      queryKey: getDataDesignerGetJobQueryKey(workspace, name),
      queryFn: ({ signal }) => dataDesignerGetJob(workspace, name, signal),
      enabled: !!(workspace && name),
      ...options?.query,
    },
    queryClient
  );

export const dataDesignerDeleteJob = (workspace: string, name: string, signal?: AbortSignal) =>
  customFetch<void>({
    url: dataDesignerJobPath(workspace, `/${encodeURIComponent(String(name))}`),
    method: 'DELETE',
    signal,
  });

export const useDataDesignerDeleteJob = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(
  options?: MutationOptions<
    Awaited<ReturnType<typeof dataDesignerDeleteJob>>,
    { workspace: string; name: string },
    TError,
    TContext
  >,
  queryClient?: QueryClient
): UseMutationResult<
  Awaited<ReturnType<typeof dataDesignerDeleteJob>>,
  TError,
  { workspace: string; name: string },
  TContext
> =>
  useMutation(
    {
      mutationKey: ['dataDesignerDeleteJob'],
      mutationFn: ({ workspace, name }) => dataDesignerDeleteJob(workspace, name),
      ...options?.mutation,
    },
    queryClient
  );

export const dataDesignerCancelJob = (workspace: string, name: string, signal?: AbortSignal) =>
  customFetch<DataDesignerJob>({
    url: dataDesignerJobPath(workspace, `/${encodeURIComponent(String(name))}/cancel`),
    method: 'POST',
    signal,
  });

export const useDataDesignerCancelJob = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(
  options?: MutationOptions<
    Awaited<ReturnType<typeof dataDesignerCancelJob>>,
    { workspace: string; name: string },
    TError,
    TContext
  >,
  queryClient?: QueryClient
): UseMutationResult<
  Awaited<ReturnType<typeof dataDesignerCancelJob>>,
  TError,
  { workspace: string; name: string },
  TContext
> =>
  useMutation(
    {
      mutationKey: ['dataDesignerCancelJob'],
      mutationFn: ({ workspace, name }) => dataDesignerCancelJob(workspace, name),
      ...options?.mutation,
    },
    queryClient
  );

export const dataDesignerListJobResults = (workspace: string, name: string, signal?: AbortSignal) =>
  customFetch<DataDesignerJobResultsPage>({
    url: dataDesignerJobPath(workspace, `/${encodeURIComponent(String(name))}/results`),
    method: 'GET',
    signal,
  });

export const getDataDesignerListJobResultsQueryKey = (workspace: string, name: string) =>
  ['dataDesigner', 'jobResults', workspace, name] as const;

export const useDataDesignerListJobResults = <TError = ErrorType<HTTPValidationError>>(
  workspace: string,
  name: string,
  options?: QueryOptions<Awaited<ReturnType<typeof dataDesignerListJobResults>>, TError>,
  queryClient?: QueryClient
): UseQueryResult<Awaited<ReturnType<typeof dataDesignerListJobResults>>, TError> =>
  useQuery(
    {
      queryKey: getDataDesignerListJobResultsQueryKey(workspace, name),
      queryFn: ({ signal }) => dataDesignerListJobResults(workspace, name, signal),
      enabled: !!(workspace && name),
      ...options?.query,
    },
    queryClient
  );
