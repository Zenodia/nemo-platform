// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// TEMP: customizer-specific React Query hooks and fetchers inlined while the customizer SDK is being rebuilt.
// Source: lines 5560-7530 of @nemo/sdk/generated/platform/api.ts (verbatim).
// Restore SDK imports (`@nemo/sdk/generated/platform/api`) once the SDK regenerates with customizer support.
//
// Note: these hooks call /apis/customization/v2/... endpoints that won't exist while the customizer
// service is removed. The customizer UI is feature-flagged off, so they should never be invoked at runtime.

import { useMutation, useQuery, useSuspenseQuery } from '@tanstack/react-query';
import type {
  DataTag,
  DefinedInitialDataOptions,
  DefinedUseQueryResult,
  MutationFunction,
  QueryClient,
  QueryFunction,
  QueryKey,
  UndefinedInitialDataOptions,
  UseMutationOptions,
  UseMutationResult,
  UseQueryOptions,
  UseQueryResult,
  UseSuspenseQueryOptions,
  UseSuspenseQueryResult,
} from '@tanstack/react-query';

import { customFetch } from '../../generated/fetchers/platform';
import type { ErrorType } from '../../generated/fetchers/platform';

// Non-customizer schema types still in the SDK
import type {
  HTTPValidationError,
  PlatformJobListResultResponse,
  PlatformJobLogPage,
  PlatformJobResultResponse,
  PlatformJobStatusResponse,
} from '../../generated/platform/schema';

// Customizer-specific schema types — inlined locally
import type {
  CustomizationGetJobLogsParams,
  CustomizationJob,
  CustomizationJobRequest,
  CustomizationJobsPage,
  CustomizationListJobsParams,
} from './schema';

/**
 * @summary Create Job
 */
export const customizationCreateJob = (
  workspace: string,
  customizationJobRequest: CustomizationJobRequest,
  signal?: AbortSignal
) => {
  return customFetch<CustomizationJob>({
    url: `/apis/customization/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs`,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: customizationJobRequest,
    signal,
  });
};

export const getCustomizationCreateJobMutationOptions = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(options?: {
  mutation?: UseMutationOptions<
    Awaited<ReturnType<typeof customizationCreateJob>>,
    TError,
    { workspace: string; data: CustomizationJobRequest },
    TContext
  >;
}): UseMutationOptions<
  Awaited<ReturnType<typeof customizationCreateJob>>,
  TError,
  { workspace: string; data: CustomizationJobRequest },
  TContext
> => {
  const mutationKey = ['customizationCreateJob'];
  const { mutation: mutationOptions } = options
    ? options.mutation && 'mutationKey' in options.mutation && options.mutation.mutationKey
      ? options
      : { ...options, mutation: { ...options.mutation, mutationKey } }
    : { mutation: { mutationKey } };

  const mutationFn: MutationFunction<
    Awaited<ReturnType<typeof customizationCreateJob>>,
    { workspace: string; data: CustomizationJobRequest }
  > = (props) => {
    const { workspace, data } = props ?? {};

    return customizationCreateJob(workspace, data);
  };

  return { mutationFn, ...mutationOptions };
};

export type CustomizationCreateJobMutationResult = NonNullable<
  Awaited<ReturnType<typeof customizationCreateJob>>
>;
export type CustomizationCreateJobMutationBody = CustomizationJobRequest;
export type CustomizationCreateJobMutationError = ErrorType<HTTPValidationError>;

/**
 * @summary Create Job
 */
export const useCustomizationCreateJob = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(
  options?: {
    mutation?: UseMutationOptions<
      Awaited<ReturnType<typeof customizationCreateJob>>,
      TError,
      { workspace: string; data: CustomizationJobRequest },
      TContext
    >;
  },
  queryClient?: QueryClient
): UseMutationResult<
  Awaited<ReturnType<typeof customizationCreateJob>>,
  TError,
  { workspace: string; data: CustomizationJobRequest },
  TContext
> => {
  return useMutation(getCustomizationCreateJobMutationOptions(options), queryClient);
};

/**
 * @summary List Jobs
 */
export const customizationListJobs = (
  workspace: string,
  params?: CustomizationListJobsParams,
  signal?: AbortSignal
) => {
  return customFetch<CustomizationJobsPage>({
    url: `/apis/customization/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs`,
    method: 'GET',
    params,
    signal,
  });
};

export const getCustomizationListJobsQueryKey = (
  workspace: string,
  params?: CustomizationListJobsParams
) => {
  return [
    `/apis/customization/v2/workspaces/${workspace}/jobs`,
    ...(params ? [params] : []),
  ] as const;
};

export const getCustomizationListJobsQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: CustomizationListJobsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationListJobs>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getCustomizationListJobsQueryKey(workspace, params);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationListJobs>>> = ({ signal }) =>
    customizationListJobs(workspace, params, signal);

  return { queryKey, queryFn, enabled: !!workspace, ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof customizationListJobs>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationListJobsQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationListJobs>>
>;
export type CustomizationListJobsQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationListJobs<
  TData = Awaited<ReturnType<typeof customizationListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params: undefined | CustomizationListJobsParams,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationListJobs>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationListJobs>>,
          TError,
          Awaited<ReturnType<typeof customizationListJobs>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationListJobs<
  TData = Awaited<ReturnType<typeof customizationListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: CustomizationListJobsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationListJobs>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationListJobs>>,
          TError,
          Awaited<ReturnType<typeof customizationListJobs>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationListJobs<
  TData = Awaited<ReturnType<typeof customizationListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: CustomizationListJobsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary List Jobs
 */

export function useCustomizationListJobs<
  TData = Awaited<ReturnType<typeof customizationListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: CustomizationListJobsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationListJobsQueryOptions(workspace, params, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getCustomizationListJobsSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: CustomizationListJobsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationListJobs>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getCustomizationListJobsQueryKey(workspace, params);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationListJobs>>> = ({ signal }) =>
    customizationListJobs(workspace, params, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof customizationListJobs>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationListJobsSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationListJobs>>
>;
export type CustomizationListJobsSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationListJobsSuspense<
  TData = Awaited<ReturnType<typeof customizationListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params: undefined | CustomizationListJobsParams,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationListJobsSuspense<
  TData = Awaited<ReturnType<typeof customizationListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: CustomizationListJobsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationListJobsSuspense<
  TData = Awaited<ReturnType<typeof customizationListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: CustomizationListJobsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary List Jobs
 */

export function useCustomizationListJobsSuspense<
  TData = Awaited<ReturnType<typeof customizationListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: CustomizationListJobsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationListJobsSuspenseQueryOptions(workspace, params, options);

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Get Job Result
 */
export const customizationGetJobResult = (
  workspace: string,
  job: string,
  name: string,
  signal?: AbortSignal
) => {
  return customFetch<PlatformJobResultResponse>({
    url: `/apis/customization/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(job))}/results/${encodeURIComponent(String(name))}`,
    method: 'GET',
    signal,
  });
};

export const getCustomizationGetJobResultQueryKey = (
  workspace: string,
  job: string,
  name: string
) => {
  return [`/apis/customization/v2/workspaces/${workspace}/jobs/${job}/results/${name}`] as const;
};

export const getCustomizationGetJobResultQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getCustomizationGetJobResultQueryKey(workspace, job, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationGetJobResult>>> = ({
    signal,
  }) => customizationGetJobResult(workspace, job, name, signal);

  return {
    queryKey,
    queryFn,
    enabled: !!(workspace && job && name),
    ...queryOptions,
  } as UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };
};

export type CustomizationGetJobResultQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationGetJobResult>>
>;
export type CustomizationGetJobResultQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationGetJobResult<
  TData = Awaited<ReturnType<typeof customizationGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationGetJobResult>>,
          TError,
          Awaited<ReturnType<typeof customizationGetJobResult>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobResult<
  TData = Awaited<ReturnType<typeof customizationGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationGetJobResult>>,
          TError,
          Awaited<ReturnType<typeof customizationGetJobResult>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobResult<
  TData = Awaited<ReturnType<typeof customizationGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Result
 */

export function useCustomizationGetJobResult<
  TData = Awaited<ReturnType<typeof customizationGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationGetJobResultQueryOptions(workspace, job, name, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getCustomizationGetJobResultSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getCustomizationGetJobResultQueryKey(workspace, job, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationGetJobResult>>> = ({
    signal,
  }) => customizationGetJobResult(workspace, job, name, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof customizationGetJobResult>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationGetJobResultSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationGetJobResult>>
>;
export type CustomizationGetJobResultSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationGetJobResultSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobResultSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobResultSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Result
 */

export function useCustomizationGetJobResultSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationGetJobResultSuspenseQueryOptions(
    workspace,
    job,
    name,
    options
  );

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Download Job Result
 */
export const customizationDownloadJobResult = (
  workspace: string,
  job: string,
  name: string,
  signal?: AbortSignal
) => {
  return customFetch<Blob>({
    url: `/apis/customization/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(job))}/results/${encodeURIComponent(String(name))}/download`,
    method: 'GET',
    responseType: 'blob',
    signal,
  });
};

export const getCustomizationDownloadJobResultQueryKey = (
  workspace: string,
  job: string,
  name: string
) => {
  return [
    `/apis/customization/v2/workspaces/${workspace}/jobs/${job}/results/${name}/download`,
  ] as const;
};

export const getCustomizationDownloadJobResultQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationDownloadJobResult>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getCustomizationDownloadJobResultQueryKey(workspace, job, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationDownloadJobResult>>> = ({
    signal,
  }) => customizationDownloadJobResult(workspace, job, name, signal);

  return {
    queryKey,
    queryFn,
    enabled: !!(workspace && job && name),
    ...queryOptions,
  } as UseQueryOptions<
    Awaited<ReturnType<typeof customizationDownloadJobResult>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationDownloadJobResultQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationDownloadJobResult>>
>;
export type CustomizationDownloadJobResultQueryError = ErrorType<void | HTTPValidationError>;

export function useCustomizationDownloadJobResult<
  TData = Awaited<ReturnType<typeof customizationDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationDownloadJobResult>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationDownloadJobResult>>,
          TError,
          Awaited<ReturnType<typeof customizationDownloadJobResult>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationDownloadJobResult<
  TData = Awaited<ReturnType<typeof customizationDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationDownloadJobResult>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationDownloadJobResult>>,
          TError,
          Awaited<ReturnType<typeof customizationDownloadJobResult>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationDownloadJobResult<
  TData = Awaited<ReturnType<typeof customizationDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationDownloadJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result
 */

export function useCustomizationDownloadJobResult<
  TData = Awaited<ReturnType<typeof customizationDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationDownloadJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationDownloadJobResultQueryOptions(workspace, job, name, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getCustomizationDownloadJobResultSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof customizationDownloadJobResult>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getCustomizationDownloadJobResultQueryKey(workspace, job, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationDownloadJobResult>>> = ({
    signal,
  }) => customizationDownloadJobResult(workspace, job, name, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof customizationDownloadJobResult>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationDownloadJobResultSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationDownloadJobResult>>
>;
export type CustomizationDownloadJobResultSuspenseQueryError =
  ErrorType<void | HTTPValidationError>;

export function useCustomizationDownloadJobResultSuspense<
  TData = Awaited<ReturnType<typeof customizationDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof customizationDownloadJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationDownloadJobResultSuspense<
  TData = Awaited<ReturnType<typeof customizationDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof customizationDownloadJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationDownloadJobResultSuspense<
  TData = Awaited<ReturnType<typeof customizationDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof customizationDownloadJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result
 */

export function useCustomizationDownloadJobResultSuspense<
  TData = Awaited<ReturnType<typeof customizationDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof customizationDownloadJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationDownloadJobResultSuspenseQueryOptions(
    workspace,
    job,
    name,
    options
  );

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Get Job
 */
export const customizationGetJob = (workspace: string, name: string, signal?: AbortSignal) => {
  return customFetch<CustomizationJob>({
    url: `/apis/customization/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}`,
    method: 'GET',
    signal,
  });
};

export const getCustomizationGetJobQueryKey = (workspace: string, name: string) => {
  return [`/apis/customization/v2/workspaces/${workspace}/jobs/${name}`] as const;
};

export const getCustomizationGetJobQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJob>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getCustomizationGetJobQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationGetJob>>> = ({ signal }) =>
    customizationGetJob(workspace, name, signal);

  return { queryKey, queryFn, enabled: !!(workspace && name), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof customizationGetJob>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationGetJobQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationGetJob>>
>;
export type CustomizationGetJobQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationGetJob<
  TData = Awaited<ReturnType<typeof customizationGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJob>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationGetJob>>,
          TError,
          Awaited<ReturnType<typeof customizationGetJob>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJob<
  TData = Awaited<ReturnType<typeof customizationGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJob>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationGetJob>>,
          TError,
          Awaited<ReturnType<typeof customizationGetJob>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJob<
  TData = Awaited<ReturnType<typeof customizationGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job
 */

export function useCustomizationGetJob<
  TData = Awaited<ReturnType<typeof customizationGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationGetJobQueryOptions(workspace, name, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getCustomizationGetJobSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJob>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getCustomizationGetJobQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationGetJob>>> = ({ signal }) =>
    customizationGetJob(workspace, name, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof customizationGetJob>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationGetJobSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationGetJob>>
>;
export type CustomizationGetJobSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationGetJobSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job
 */

export function useCustomizationGetJobSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationGetJobSuspenseQueryOptions(workspace, name, options);

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Delete Job
 */
export const customizationDeleteJob = (workspace: string, name: string, signal?: AbortSignal) => {
  return customFetch<void>({
    url: `/apis/customization/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}`,
    method: 'DELETE',
    signal,
  });
};

export const getCustomizationDeleteJobMutationOptions = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(options?: {
  mutation?: UseMutationOptions<
    Awaited<ReturnType<typeof customizationDeleteJob>>,
    TError,
    { workspace: string; name: string },
    TContext
  >;
}): UseMutationOptions<
  Awaited<ReturnType<typeof customizationDeleteJob>>,
  TError,
  { workspace: string; name: string },
  TContext
> => {
  const mutationKey = ['customizationDeleteJob'];
  const { mutation: mutationOptions } = options
    ? options.mutation && 'mutationKey' in options.mutation && options.mutation.mutationKey
      ? options
      : { ...options, mutation: { ...options.mutation, mutationKey } }
    : { mutation: { mutationKey } };

  const mutationFn: MutationFunction<
    Awaited<ReturnType<typeof customizationDeleteJob>>,
    { workspace: string; name: string }
  > = (props) => {
    const { workspace, name } = props ?? {};

    return customizationDeleteJob(workspace, name);
  };

  return { mutationFn, ...mutationOptions };
};

export type CustomizationDeleteJobMutationResult = NonNullable<
  Awaited<ReturnType<typeof customizationDeleteJob>>
>;

export type CustomizationDeleteJobMutationError = ErrorType<HTTPValidationError>;

/**
 * @summary Delete Job
 */
export const useCustomizationDeleteJob = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(
  options?: {
    mutation?: UseMutationOptions<
      Awaited<ReturnType<typeof customizationDeleteJob>>,
      TError,
      { workspace: string; name: string },
      TContext
    >;
  },
  queryClient?: QueryClient
): UseMutationResult<
  Awaited<ReturnType<typeof customizationDeleteJob>>,
  TError,
  { workspace: string; name: string },
  TContext
> => {
  return useMutation(getCustomizationDeleteJobMutationOptions(options), queryClient);
};

/**
 * @summary Cancel Job
 */
export const customizationCancelJob = (workspace: string, name: string, signal?: AbortSignal) => {
  return customFetch<CustomizationJob>({
    url: `/apis/customization/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}/cancel`,
    method: 'POST',
    signal,
  });
};

export const getCustomizationCancelJobMutationOptions = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(options?: {
  mutation?: UseMutationOptions<
    Awaited<ReturnType<typeof customizationCancelJob>>,
    TError,
    { workspace: string; name: string },
    TContext
  >;
}): UseMutationOptions<
  Awaited<ReturnType<typeof customizationCancelJob>>,
  TError,
  { workspace: string; name: string },
  TContext
> => {
  const mutationKey = ['customizationCancelJob'];
  const { mutation: mutationOptions } = options
    ? options.mutation && 'mutationKey' in options.mutation && options.mutation.mutationKey
      ? options
      : { ...options, mutation: { ...options.mutation, mutationKey } }
    : { mutation: { mutationKey } };

  const mutationFn: MutationFunction<
    Awaited<ReturnType<typeof customizationCancelJob>>,
    { workspace: string; name: string }
  > = (props) => {
    const { workspace, name } = props ?? {};

    return customizationCancelJob(workspace, name);
  };

  return { mutationFn, ...mutationOptions };
};

export type CustomizationCancelJobMutationResult = NonNullable<
  Awaited<ReturnType<typeof customizationCancelJob>>
>;

export type CustomizationCancelJobMutationError = ErrorType<HTTPValidationError>;

/**
 * @summary Cancel Job
 */
export const useCustomizationCancelJob = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(
  options?: {
    mutation?: UseMutationOptions<
      Awaited<ReturnType<typeof customizationCancelJob>>,
      TError,
      { workspace: string; name: string },
      TContext
    >;
  },
  queryClient?: QueryClient
): UseMutationResult<
  Awaited<ReturnType<typeof customizationCancelJob>>,
  TError,
  { workspace: string; name: string },
  TContext
> => {
  return useMutation(getCustomizationCancelJobMutationOptions(options), queryClient);
};

/**
 * @summary Get Job Logs
 */
export const customizationGetJobLogs = (
  workspace: string,
  name: string,
  params?: CustomizationGetJobLogsParams,
  signal?: AbortSignal
) => {
  return customFetch<PlatformJobLogPage>({
    url: `/apis/customization/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}/logs`,
    method: 'GET',
    params,
    signal,
  });
};

export const getCustomizationGetJobLogsQueryKey = (
  workspace: string,
  name: string,
  params?: CustomizationGetJobLogsParams
) => {
  return [
    `/apis/customization/v2/workspaces/${workspace}/jobs/${name}/logs`,
    ...(params ? [params] : []),
  ] as const;
};

export const getCustomizationGetJobLogsQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: CustomizationGetJobLogsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobLogs>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getCustomizationGetJobLogsQueryKey(workspace, name, params);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationGetJobLogs>>> = ({
    signal,
  }) => customizationGetJobLogs(workspace, name, params, signal);

  return { queryKey, queryFn, enabled: !!(workspace && name), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof customizationGetJobLogs>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationGetJobLogsQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationGetJobLogs>>
>;
export type CustomizationGetJobLogsQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationGetJobLogs<
  TData = Awaited<ReturnType<typeof customizationGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params: undefined | CustomizationGetJobLogsParams,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobLogs>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationGetJobLogs>>,
          TError,
          Awaited<ReturnType<typeof customizationGetJobLogs>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobLogs<
  TData = Awaited<ReturnType<typeof customizationGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: CustomizationGetJobLogsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobLogs>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationGetJobLogs>>,
          TError,
          Awaited<ReturnType<typeof customizationGetJobLogs>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobLogs<
  TData = Awaited<ReturnType<typeof customizationGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: CustomizationGetJobLogsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Logs
 */

export function useCustomizationGetJobLogs<
  TData = Awaited<ReturnType<typeof customizationGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: CustomizationGetJobLogsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationGetJobLogsQueryOptions(workspace, name, params, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getCustomizationGetJobLogsSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: CustomizationGetJobLogsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobLogs>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getCustomizationGetJobLogsQueryKey(workspace, name, params);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationGetJobLogs>>> = ({
    signal,
  }) => customizationGetJobLogs(workspace, name, params, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof customizationGetJobLogs>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationGetJobLogsSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationGetJobLogs>>
>;
export type CustomizationGetJobLogsSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationGetJobLogsSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params: undefined | CustomizationGetJobLogsParams,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobLogsSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: CustomizationGetJobLogsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobLogsSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: CustomizationGetJobLogsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Logs
 */

export function useCustomizationGetJobLogsSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: CustomizationGetJobLogsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationGetJobLogsSuspenseQueryOptions(
    workspace,
    name,
    params,
    options
  );

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary List Job Results
 */
export const customizationListJobResults = (
  workspace: string,
  name: string,
  signal?: AbortSignal
) => {
  return customFetch<PlatformJobListResultResponse>({
    url: `/apis/customization/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}/results`,
    method: 'GET',
    signal,
  });
};

export const getCustomizationListJobResultsQueryKey = (workspace: string, name: string) => {
  return [`/apis/customization/v2/workspaces/${workspace}/jobs/${name}/results`] as const;
};

export const getCustomizationListJobResultsQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationListJobResults>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getCustomizationListJobResultsQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationListJobResults>>> = ({
    signal,
  }) => customizationListJobResults(workspace, name, signal);

  return { queryKey, queryFn, enabled: !!(workspace && name), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof customizationListJobResults>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationListJobResultsQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationListJobResults>>
>;
export type CustomizationListJobResultsQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationListJobResults<
  TData = Awaited<ReturnType<typeof customizationListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationListJobResults>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationListJobResults>>,
          TError,
          Awaited<ReturnType<typeof customizationListJobResults>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationListJobResults<
  TData = Awaited<ReturnType<typeof customizationListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationListJobResults>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationListJobResults>>,
          TError,
          Awaited<ReturnType<typeof customizationListJobResults>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationListJobResults<
  TData = Awaited<ReturnType<typeof customizationListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationListJobResults>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary List Job Results
 */

export function useCustomizationListJobResults<
  TData = Awaited<ReturnType<typeof customizationListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationListJobResults>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationListJobResultsQueryOptions(workspace, name, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getCustomizationListJobResultsSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof customizationListJobResults>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getCustomizationListJobResultsQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationListJobResults>>> = ({
    signal,
  }) => customizationListJobResults(workspace, name, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof customizationListJobResults>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationListJobResultsSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationListJobResults>>
>;
export type CustomizationListJobResultsSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationListJobResultsSuspense<
  TData = Awaited<ReturnType<typeof customizationListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof customizationListJobResults>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationListJobResultsSuspense<
  TData = Awaited<ReturnType<typeof customizationListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof customizationListJobResults>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationListJobResultsSuspense<
  TData = Awaited<ReturnType<typeof customizationListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof customizationListJobResults>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary List Job Results
 */

export function useCustomizationListJobResultsSuspense<
  TData = Awaited<ReturnType<typeof customizationListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof customizationListJobResults>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationListJobResultsSuspenseQueryOptions(workspace, name, options);

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Get Job Status
 */
export const customizationGetJobStatus = (
  workspace: string,
  name: string,
  signal?: AbortSignal
) => {
  return customFetch<PlatformJobStatusResponse>({
    url: `/apis/customization/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}/status`,
    method: 'GET',
    signal,
  });
};

export const getCustomizationGetJobStatusQueryKey = (workspace: string, name: string) => {
  return [`/apis/customization/v2/workspaces/${workspace}/jobs/${name}/status`] as const;
};

export const getCustomizationGetJobStatusQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobStatus>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getCustomizationGetJobStatusQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationGetJobStatus>>> = ({
    signal,
  }) => customizationGetJobStatus(workspace, name, signal);

  return { queryKey, queryFn, enabled: !!(workspace && name), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof customizationGetJobStatus>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationGetJobStatusQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationGetJobStatus>>
>;
export type CustomizationGetJobStatusQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationGetJobStatus<
  TData = Awaited<ReturnType<typeof customizationGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobStatus>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationGetJobStatus>>,
          TError,
          Awaited<ReturnType<typeof customizationGetJobStatus>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobStatus<
  TData = Awaited<ReturnType<typeof customizationGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobStatus>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof customizationGetJobStatus>>,
          TError,
          Awaited<ReturnType<typeof customizationGetJobStatus>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobStatus<
  TData = Awaited<ReturnType<typeof customizationGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobStatus>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Status
 */

export function useCustomizationGetJobStatus<
  TData = Awaited<ReturnType<typeof customizationGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof customizationGetJobStatus>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationGetJobStatusQueryOptions(workspace, name, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getCustomizationGetJobStatusSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof customizationGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobStatus>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getCustomizationGetJobStatusQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof customizationGetJobStatus>>> = ({
    signal,
  }) => customizationGetJobStatus(workspace, name, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof customizationGetJobStatus>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type CustomizationGetJobStatusSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof customizationGetJobStatus>>
>;
export type CustomizationGetJobStatusSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useCustomizationGetJobStatusSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobStatus>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobStatusSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobStatus>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useCustomizationGetJobStatusSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobStatus>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Status
 */

export function useCustomizationGetJobStatusSuspense<
  TData = Awaited<ReturnType<typeof customizationGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof customizationGetJobStatus>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getCustomizationGetJobStatusSuspenseQueryOptions(workspace, name, options);

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}
