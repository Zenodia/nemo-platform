// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// TEMP: SafeSynthesizer-specific React Query hooks and fetchers inlined while the safe-synthesizer SDK is being rebuilt.
// Source: lines 34765-37944 of @nemo/sdk/generated/platform/api.ts (verbatim).
// Restore SDK imports (`@nemo/sdk/generated/platform/api`) once the SDK regenerates with safe-synthesizer support.

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

// Non-SafeSynthesizer schema types still in the SDK
import type {
  HTTPValidationError,
  PlatformJobListResultResponse,
  PlatformJobLogPage,
  PlatformJobResultResponse,
  PlatformJobStatusResponse,
} from '../../generated/platform/schema';

// SafeSynthesizer-specific schema types — inlined locally
import type {
  SafeSynthesizerGetJobLogsParams,
  SafeSynthesizerJob,
  SafeSynthesizerJobRequest,
  SafeSynthesizerJobsPage,
  SafeSynthesizerListJobsParams,
  SafeSynthesizerSummary,
} from './schema';

/**
 * @summary Create Job
 */
export const safeSynthesizerCreateJob = (
  workspace: string,
  safeSynthesizerJobRequest: SafeSynthesizerJobRequest,
  signal?: AbortSignal
) => {
  return customFetch<SafeSynthesizerJob>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs`,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: safeSynthesizerJobRequest,
    signal,
  });
};

export const getSafeSynthesizerCreateJobMutationOptions = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(options?: {
  mutation?: UseMutationOptions<
    Awaited<ReturnType<typeof safeSynthesizerCreateJob>>,
    TError,
    { workspace: string; data: SafeSynthesizerJobRequest },
    TContext
  >;
}): UseMutationOptions<
  Awaited<ReturnType<typeof safeSynthesizerCreateJob>>,
  TError,
  { workspace: string; data: SafeSynthesizerJobRequest },
  TContext
> => {
  const mutationKey = ['safeSynthesizerCreateJob'];
  const { mutation: mutationOptions } = options
    ? options.mutation && 'mutationKey' in options.mutation && options.mutation.mutationKey
      ? options
      : { ...options, mutation: { ...options.mutation, mutationKey } }
    : { mutation: { mutationKey } };

  const mutationFn: MutationFunction<
    Awaited<ReturnType<typeof safeSynthesizerCreateJob>>,
    { workspace: string; data: SafeSynthesizerJobRequest }
  > = (props) => {
    const { workspace, data } = props ?? {};

    return safeSynthesizerCreateJob(workspace, data);
  };

  return { mutationFn, ...mutationOptions };
};

export type SafeSynthesizerCreateJobMutationResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerCreateJob>>
>;
export type SafeSynthesizerCreateJobMutationBody = SafeSynthesizerJobRequest;
export type SafeSynthesizerCreateJobMutationError = ErrorType<HTTPValidationError>;

/**
 * @summary Create Job
 */
export const useSafeSynthesizerCreateJob = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(
  options?: {
    mutation?: UseMutationOptions<
      Awaited<ReturnType<typeof safeSynthesizerCreateJob>>,
      TError,
      { workspace: string; data: SafeSynthesizerJobRequest },
      TContext
    >;
  },
  queryClient?: QueryClient
): UseMutationResult<
  Awaited<ReturnType<typeof safeSynthesizerCreateJob>>,
  TError,
  { workspace: string; data: SafeSynthesizerJobRequest },
  TContext
> => {
  return useMutation(getSafeSynthesizerCreateJobMutationOptions(options), queryClient);
};

/**
 * @summary List Jobs
 */
export const safeSynthesizerListJobs = (
  workspace: string,
  params?: SafeSynthesizerListJobsParams,
  signal?: AbortSignal
) => {
  return customFetch<SafeSynthesizerJobsPage>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs`,
    method: 'GET',
    params,
    signal,
  });
};

export const getSafeSynthesizerListJobsQueryKey = (
  workspace: string,
  params?: SafeSynthesizerListJobsParams
) => {
  return [
    `/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs`,
    ...(params ? [params] : []),
  ] as const;
};

export const getSafeSynthesizerListJobsQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: SafeSynthesizerListJobsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobs>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getSafeSynthesizerListJobsQueryKey(workspace, params);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerListJobs>>> = ({
    signal,
  }) => safeSynthesizerListJobs(workspace, params, signal);

  return { queryKey, queryFn, enabled: !!workspace, ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerListJobsQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerListJobs>>
>;
export type SafeSynthesizerListJobsQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerListJobs<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params: undefined | SafeSynthesizerListJobsParams,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobs>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerListJobs>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerListJobs<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: SafeSynthesizerListJobsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobs>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerListJobs>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerListJobs<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: SafeSynthesizerListJobsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary List Jobs
 */

export function useSafeSynthesizerListJobs<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: SafeSynthesizerListJobsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerListJobsQueryOptions(workspace, params, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerListJobsSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: SafeSynthesizerListJobsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobs>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getSafeSynthesizerListJobsQueryKey(workspace, params);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerListJobs>>> = ({
    signal,
  }) => safeSynthesizerListJobs(workspace, params, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerListJobsSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerListJobs>>
>;
export type SafeSynthesizerListJobsSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerListJobsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params: undefined | SafeSynthesizerListJobsParams,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerListJobsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: SafeSynthesizerListJobsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerListJobsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: SafeSynthesizerListJobsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary List Jobs
 */

export function useSafeSynthesizerListJobsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  params?: SafeSynthesizerListJobsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerListJobsSuspenseQueryOptions(workspace, params, options);

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Download Job Result Adapter
 */
export const safeSynthesizerDownloadJobResultAdapter = (
  workspace: string,
  job: string,
  signal?: AbortSignal
) => {
  return customFetch<Blob>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(job))}/results/adapter/download`,
    method: 'GET',
    responseType: 'blob',
    signal,
  });
};

export const getSafeSynthesizerDownloadJobResultAdapterQueryKey = (
  workspace: string,
  job: string
) => {
  return [
    `/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs/${job}/results/adapter/download`,
  ] as const;
};

export const getSafeSynthesizerDownloadJobResultAdapterQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerDownloadJobResultAdapterQueryKey(workspace, job);

  const queryFn: QueryFunction<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>
  > = ({ signal }) => safeSynthesizerDownloadJobResultAdapter(workspace, job, signal);

  return { queryKey, queryFn, enabled: !!(workspace && job), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerDownloadJobResultAdapterQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>
>;
export type SafeSynthesizerDownloadJobResultAdapterQueryError =
  ErrorType<void | HTTPValidationError>;

export function useSafeSynthesizerDownloadJobResultAdapter<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options: {
    query: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
        TError,
        TData
      >
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultAdapter<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
        TError,
        TData
      >
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultAdapter<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result Adapter
 */

export function useSafeSynthesizerDownloadJobResultAdapter<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerDownloadJobResultAdapterQueryOptions(
    workspace,
    job,
    options
  );

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerDownloadJobResultAdapterSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerDownloadJobResultAdapterQueryKey(workspace, job);

  const queryFn: QueryFunction<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>
  > = ({ signal }) => safeSynthesizerDownloadJobResultAdapter(workspace, job, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerDownloadJobResultAdapterSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>
>;
export type SafeSynthesizerDownloadJobResultAdapterSuspenseQueryError =
  ErrorType<void | HTTPValidationError>;

export function useSafeSynthesizerDownloadJobResultAdapterSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultAdapterSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultAdapterSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result Adapter
 */

export function useSafeSynthesizerDownloadJobResultAdapterSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultAdapter>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerDownloadJobResultAdapterSuspenseQueryOptions(
    workspace,
    job,
    options
  );

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Download Job Result Evaluation-Report
 */
export const safeSynthesizerDownloadJobResultEvaluationReport = (
  workspace: string,
  job: string,
  signal?: AbortSignal
) => {
  return customFetch<Blob>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(job))}/results/evaluation-report/download`,
    method: 'GET',
    responseType: 'blob',
    signal,
  });
};

export const getSafeSynthesizerDownloadJobResultEvaluationReportQueryKey = (
  workspace: string,
  job: string
) => {
  return [
    `/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs/${job}/results/evaluation-report/download`,
  ] as const;
};

export const getSafeSynthesizerDownloadJobResultEvaluationReportQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ??
    getSafeSynthesizerDownloadJobResultEvaluationReportQueryKey(workspace, job);

  const queryFn: QueryFunction<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>
  > = ({ signal }) => safeSynthesizerDownloadJobResultEvaluationReport(workspace, job, signal);

  return { queryKey, queryFn, enabled: !!(workspace && job), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerDownloadJobResultEvaluationReportQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>
>;
export type SafeSynthesizerDownloadJobResultEvaluationReportQueryError =
  ErrorType<void | HTTPValidationError>;

export function useSafeSynthesizerDownloadJobResultEvaluationReport<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options: {
    query: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
        TError,
        TData
      >
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultEvaluationReport<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
        TError,
        TData
      >
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultEvaluationReport<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result Evaluation-Report
 */

export function useSafeSynthesizerDownloadJobResultEvaluationReport<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerDownloadJobResultEvaluationReportQueryOptions(
    workspace,
    job,
    options
  );

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerDownloadJobResultEvaluationReportSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ??
    getSafeSynthesizerDownloadJobResultEvaluationReportQueryKey(workspace, job);

  const queryFn: QueryFunction<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>
  > = ({ signal }) => safeSynthesizerDownloadJobResultEvaluationReport(workspace, job, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerDownloadJobResultEvaluationReportSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>
>;
export type SafeSynthesizerDownloadJobResultEvaluationReportSuspenseQueryError =
  ErrorType<void | HTTPValidationError>;

export function useSafeSynthesizerDownloadJobResultEvaluationReportSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultEvaluationReportSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultEvaluationReportSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result Evaluation-Report
 */

export function useSafeSynthesizerDownloadJobResultEvaluationReportSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultEvaluationReport>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerDownloadJobResultEvaluationReportSuspenseQueryOptions(
    workspace,
    job,
    options
  );

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Download Job Result Summary
 */
export const safeSynthesizerDownloadJobResultSummary = (
  workspace: string,
  job: string,
  signal?: AbortSignal
) => {
  return customFetch<SafeSynthesizerSummary>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(job))}/results/summary/download`,
    method: 'GET',
    signal,
  });
};

export const getSafeSynthesizerDownloadJobResultSummaryQueryKey = (
  workspace: string,
  job: string
) => {
  return [
    `/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs/${job}/results/summary/download`,
  ] as const;
};

export const getSafeSynthesizerDownloadJobResultSummaryQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerDownloadJobResultSummaryQueryKey(workspace, job);

  const queryFn: QueryFunction<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>
  > = ({ signal }) => safeSynthesizerDownloadJobResultSummary(workspace, job, signal);

  return { queryKey, queryFn, enabled: !!(workspace && job), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerDownloadJobResultSummaryQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>
>;
export type SafeSynthesizerDownloadJobResultSummaryQueryError =
  ErrorType<void | HTTPValidationError>;

export function useSafeSynthesizerDownloadJobResultSummary<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options: {
    query: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
        TError,
        TData
      >
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultSummary<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
        TError,
        TData
      >
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultSummary<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result Summary
 */

export function useSafeSynthesizerDownloadJobResultSummary<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerDownloadJobResultSummaryQueryOptions(
    workspace,
    job,
    options
  );

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerDownloadJobResultSummarySuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerDownloadJobResultSummaryQueryKey(workspace, job);

  const queryFn: QueryFunction<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>
  > = ({ signal }) => safeSynthesizerDownloadJobResultSummary(workspace, job, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerDownloadJobResultSummarySuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>
>;
export type SafeSynthesizerDownloadJobResultSummarySuspenseQueryError =
  ErrorType<void | HTTPValidationError>;

export function useSafeSynthesizerDownloadJobResultSummarySuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultSummarySuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultSummarySuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result Summary
 */

export function useSafeSynthesizerDownloadJobResultSummarySuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSummary>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerDownloadJobResultSummarySuspenseQueryOptions(
    workspace,
    job,
    options
  );

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Download Job Result Synthetic-Data
 */
export const safeSynthesizerDownloadJobResultSyntheticData = (
  workspace: string,
  job: string,
  signal?: AbortSignal
) => {
  return customFetch<Blob>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(job))}/results/synthetic-data/download`,
    method: 'GET',
    responseType: 'blob',
    signal,
  });
};

export const getSafeSynthesizerDownloadJobResultSyntheticDataQueryKey = (
  workspace: string,
  job: string
) => {
  return [
    `/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs/${job}/results/synthetic-data/download`,
  ] as const;
};

export const getSafeSynthesizerDownloadJobResultSyntheticDataQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ??
    getSafeSynthesizerDownloadJobResultSyntheticDataQueryKey(workspace, job);

  const queryFn: QueryFunction<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>
  > = ({ signal }) => safeSynthesizerDownloadJobResultSyntheticData(workspace, job, signal);

  return { queryKey, queryFn, enabled: !!(workspace && job), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerDownloadJobResultSyntheticDataQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>
>;
export type SafeSynthesizerDownloadJobResultSyntheticDataQueryError =
  ErrorType<void | HTTPValidationError>;

export function useSafeSynthesizerDownloadJobResultSyntheticData<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options: {
    query: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
        TError,
        TData
      >
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultSyntheticData<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
        TError,
        TData
      >
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultSyntheticData<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result Synthetic-Data
 */

export function useSafeSynthesizerDownloadJobResultSyntheticData<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerDownloadJobResultSyntheticDataQueryOptions(
    workspace,
    job,
    options
  );

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerDownloadJobResultSyntheticDataSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ??
    getSafeSynthesizerDownloadJobResultSyntheticDataQueryKey(workspace, job);

  const queryFn: QueryFunction<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>
  > = ({ signal }) => safeSynthesizerDownloadJobResultSyntheticData(workspace, job, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerDownloadJobResultSyntheticDataSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>
>;
export type SafeSynthesizerDownloadJobResultSyntheticDataSuspenseQueryError =
  ErrorType<void | HTTPValidationError>;

export function useSafeSynthesizerDownloadJobResultSyntheticDataSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultSyntheticDataSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultSyntheticDataSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result Synthetic-Data
 */

export function useSafeSynthesizerDownloadJobResultSyntheticDataSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResultSyntheticData>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerDownloadJobResultSyntheticDataSuspenseQueryOptions(
    workspace,
    job,
    options
  );

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Get Job Result
 */
export const safeSynthesizerGetJobResult = (
  workspace: string,
  job: string,
  name: string,
  signal?: AbortSignal
) => {
  return customFetch<PlatformJobResultResponse>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(job))}/results/${encodeURIComponent(String(name))}`,
    method: 'GET',
    signal,
  });
};

export const getSafeSynthesizerGetJobResultQueryKey = (
  workspace: string,
  job: string,
  name: string
) => {
  return [`/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs/${job}/results/${name}`] as const;
};

export const getSafeSynthesizerGetJobResultQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerGetJobResultQueryKey(workspace, job, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>> = ({
    signal,
  }) => safeSynthesizerGetJobResult(workspace, job, name, signal);

  return {
    queryKey,
    queryFn,
    enabled: !!(workspace && job && name),
    ...queryOptions,
  } as UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>, TError, TData> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };
};

export type SafeSynthesizerGetJobResultQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>
>;
export type SafeSynthesizerGetJobResultQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerGetJobResult<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobResult<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobResult<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Result
 */

export function useSafeSynthesizerGetJobResult<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerGetJobResultQueryOptions(workspace, job, name, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerGetJobResultSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerGetJobResultQueryKey(workspace, job, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>> = ({
    signal,
  }) => safeSynthesizerGetJobResult(workspace, job, name, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerGetJobResultSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>
>;
export type SafeSynthesizerGetJobResultSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerGetJobResultSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobResultSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobResultSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Result
 */

export function useSafeSynthesizerGetJobResultSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerGetJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerGetJobResultSuspenseQueryOptions(
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
export const safeSynthesizerDownloadJobResult = (
  workspace: string,
  job: string,
  name: string,
  signal?: AbortSignal
) => {
  return customFetch<Blob>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(job))}/results/${encodeURIComponent(String(name))}/download`,
    method: 'GET',
    responseType: 'blob',
    signal,
  });
};

export const getSafeSynthesizerDownloadJobResultQueryKey = (
  workspace: string,
  job: string,
  name: string
) => {
  return [
    `/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs/${job}/results/${name}/download`,
  ] as const;
};

export const getSafeSynthesizerDownloadJobResultQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerDownloadJobResultQueryKey(workspace, job, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>> = ({
    signal,
  }) => safeSynthesizerDownloadJobResult(workspace, job, name, signal);

  return {
    queryKey,
    queryFn,
    enabled: !!(workspace && job && name),
    ...queryOptions,
  } as UseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerDownloadJobResultQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>
>;
export type SafeSynthesizerDownloadJobResultQueryError = ErrorType<void | HTTPValidationError>;

export function useSafeSynthesizerDownloadJobResult<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResult<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResult<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Download Job Result
 */

export function useSafeSynthesizerDownloadJobResult<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerDownloadJobResultQueryOptions(
    workspace,
    job,
    name,
    options
  );

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerDownloadJobResultSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerDownloadJobResultQueryKey(workspace, job, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>> = ({
    signal,
  }) => safeSynthesizerDownloadJobResult(workspace, job, name, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerDownloadJobResultSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>
>;
export type SafeSynthesizerDownloadJobResultSuspenseQueryError =
  ErrorType<void | HTTPValidationError>;

export function useSafeSynthesizerDownloadJobResultSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerDownloadJobResultSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
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

export function useSafeSynthesizerDownloadJobResultSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
  TError = ErrorType<void | HTTPValidationError>,
>(
  workspace: string,
  job: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerDownloadJobResult>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerDownloadJobResultSuspenseQueryOptions(
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
export const safeSynthesizerGetJob = (workspace: string, name: string, signal?: AbortSignal) => {
  return customFetch<SafeSynthesizerJob>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}`,
    method: 'GET',
    signal,
  });
};

export const getSafeSynthesizerGetJobQueryKey = (workspace: string, name: string) => {
  return [`/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs/${name}`] as const;
};

export const getSafeSynthesizerGetJobQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJob>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getSafeSynthesizerGetJobQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerGetJob>>> = ({ signal }) =>
    safeSynthesizerGetJob(workspace, name, signal);

  return { queryKey, queryFn, enabled: !!(workspace && name), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerGetJobQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerGetJob>>
>;
export type SafeSynthesizerGetJobQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerGetJob<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJob>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerGetJob>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJob<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJob>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerGetJob>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJob<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job
 */

export function useSafeSynthesizerGetJob<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerGetJobQueryOptions(workspace, name, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerGetJobSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJob>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getSafeSynthesizerGetJobQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerGetJob>>> = ({ signal }) =>
    safeSynthesizerGetJob(workspace, name, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerGetJobSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerGetJob>>
>;
export type SafeSynthesizerGetJobSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerGetJobSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job
 */

export function useSafeSynthesizerGetJobSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJob>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJob>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerGetJobSuspenseQueryOptions(workspace, name, options);

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}

/**
 * @summary Delete Job
 */
export const safeSynthesizerDeleteJob = (workspace: string, name: string, signal?: AbortSignal) => {
  return customFetch<void>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}`,
    method: 'DELETE',
    signal,
  });
};

export const getSafeSynthesizerDeleteJobMutationOptions = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(options?: {
  mutation?: UseMutationOptions<
    Awaited<ReturnType<typeof safeSynthesizerDeleteJob>>,
    TError,
    { workspace: string; name: string },
    TContext
  >;
}): UseMutationOptions<
  Awaited<ReturnType<typeof safeSynthesizerDeleteJob>>,
  TError,
  { workspace: string; name: string },
  TContext
> => {
  const mutationKey = ['safeSynthesizerDeleteJob'];
  const { mutation: mutationOptions } = options
    ? options.mutation && 'mutationKey' in options.mutation && options.mutation.mutationKey
      ? options
      : { ...options, mutation: { ...options.mutation, mutationKey } }
    : { mutation: { mutationKey } };

  const mutationFn: MutationFunction<
    Awaited<ReturnType<typeof safeSynthesizerDeleteJob>>,
    { workspace: string; name: string }
  > = (props) => {
    const { workspace, name } = props ?? {};

    return safeSynthesizerDeleteJob(workspace, name);
  };

  return { mutationFn, ...mutationOptions };
};

export type SafeSynthesizerDeleteJobMutationResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerDeleteJob>>
>;

export type SafeSynthesizerDeleteJobMutationError = ErrorType<HTTPValidationError>;

/**
 * @summary Delete Job
 */
export const useSafeSynthesizerDeleteJob = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(
  options?: {
    mutation?: UseMutationOptions<
      Awaited<ReturnType<typeof safeSynthesizerDeleteJob>>,
      TError,
      { workspace: string; name: string },
      TContext
    >;
  },
  queryClient?: QueryClient
): UseMutationResult<
  Awaited<ReturnType<typeof safeSynthesizerDeleteJob>>,
  TError,
  { workspace: string; name: string },
  TContext
> => {
  return useMutation(getSafeSynthesizerDeleteJobMutationOptions(options), queryClient);
};

/**
 * @summary Cancel Job
 */
export const safeSynthesizerCancelJob = (workspace: string, name: string, signal?: AbortSignal) => {
  return customFetch<SafeSynthesizerJob>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}/cancel`,
    method: 'POST',
    signal,
  });
};

export const getSafeSynthesizerCancelJobMutationOptions = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(options?: {
  mutation?: UseMutationOptions<
    Awaited<ReturnType<typeof safeSynthesizerCancelJob>>,
    TError,
    { workspace: string; name: string },
    TContext
  >;
}): UseMutationOptions<
  Awaited<ReturnType<typeof safeSynthesizerCancelJob>>,
  TError,
  { workspace: string; name: string },
  TContext
> => {
  const mutationKey = ['safeSynthesizerCancelJob'];
  const { mutation: mutationOptions } = options
    ? options.mutation && 'mutationKey' in options.mutation && options.mutation.mutationKey
      ? options
      : { ...options, mutation: { ...options.mutation, mutationKey } }
    : { mutation: { mutationKey } };

  const mutationFn: MutationFunction<
    Awaited<ReturnType<typeof safeSynthesizerCancelJob>>,
    { workspace: string; name: string }
  > = (props) => {
    const { workspace, name } = props ?? {};

    return safeSynthesizerCancelJob(workspace, name);
  };

  return { mutationFn, ...mutationOptions };
};

export type SafeSynthesizerCancelJobMutationResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerCancelJob>>
>;

export type SafeSynthesizerCancelJobMutationError = ErrorType<HTTPValidationError>;

/**
 * @summary Cancel Job
 */
export const useSafeSynthesizerCancelJob = <
  TError = ErrorType<HTTPValidationError>,
  TContext = unknown,
>(
  options?: {
    mutation?: UseMutationOptions<
      Awaited<ReturnType<typeof safeSynthesizerCancelJob>>,
      TError,
      { workspace: string; name: string },
      TContext
    >;
  },
  queryClient?: QueryClient
): UseMutationResult<
  Awaited<ReturnType<typeof safeSynthesizerCancelJob>>,
  TError,
  { workspace: string; name: string },
  TContext
> => {
  return useMutation(getSafeSynthesizerCancelJobMutationOptions(options), queryClient);
};

/**
 * @summary Get Job Logs
 */
export const safeSynthesizerGetJobLogs = (
  workspace: string,
  name: string,
  params?: SafeSynthesizerGetJobLogsParams,
  signal?: AbortSignal
) => {
  return customFetch<PlatformJobLogPage>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}/logs`,
    method: 'GET',
    params,
    signal,
  });
};

export const getSafeSynthesizerGetJobLogsQueryKey = (
  workspace: string,
  name: string,
  params?: SafeSynthesizerGetJobLogsParams
) => {
  return [
    `/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs/${name}/logs`,
    ...(params ? [params] : []),
  ] as const;
};

export const getSafeSynthesizerGetJobLogsQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: SafeSynthesizerGetJobLogsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerGetJobLogsQueryKey(workspace, name, params);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>> = ({
    signal,
  }) => safeSynthesizerGetJobLogs(workspace, name, params, signal);

  return { queryKey, queryFn, enabled: !!(workspace && name), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerGetJobLogsQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>
>;
export type SafeSynthesizerGetJobLogsQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerGetJobLogs<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params: undefined | SafeSynthesizerGetJobLogsParams,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobLogs<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: SafeSynthesizerGetJobLogsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobLogs<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: SafeSynthesizerGetJobLogsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Logs
 */

export function useSafeSynthesizerGetJobLogs<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: SafeSynthesizerGetJobLogsParams,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerGetJobLogsQueryOptions(workspace, name, params, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerGetJobLogsSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: SafeSynthesizerGetJobLogsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerGetJobLogsQueryKey(workspace, name, params);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>> = ({
    signal,
  }) => safeSynthesizerGetJobLogs(workspace, name, params, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerGetJobLogsSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>
>;
export type SafeSynthesizerGetJobLogsSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerGetJobLogsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params: undefined | SafeSynthesizerGetJobLogsParams,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobLogsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: SafeSynthesizerGetJobLogsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobLogsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: SafeSynthesizerGetJobLogsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Logs
 */

export function useSafeSynthesizerGetJobLogsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  params?: SafeSynthesizerGetJobLogsParams,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobLogs>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerGetJobLogsSuspenseQueryOptions(
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
export const safeSynthesizerListJobResults = (
  workspace: string,
  name: string,
  signal?: AbortSignal
) => {
  return customFetch<PlatformJobListResultResponse>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}/results`,
    method: 'GET',
    signal,
  });
};

export const getSafeSynthesizerListJobResultsQueryKey = (workspace: string, name: string) => {
  return [`/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs/${name}/results`] as const;
};

export const getSafeSynthesizerListJobResultsQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobResults>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerListJobResultsQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerListJobResults>>> = ({
    signal,
  }) => safeSynthesizerListJobResults(workspace, name, signal);

  return { queryKey, queryFn, enabled: !!(workspace && name), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerListJobResultsQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerListJobResults>>
>;
export type SafeSynthesizerListJobResultsQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerListJobResults<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobResults>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerListJobResults>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerListJobResults<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobResults>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerListJobResults>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerListJobResults<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobResults>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary List Job Results
 */

export function useSafeSynthesizerListJobResults<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerListJobResults>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerListJobResultsQueryOptions(workspace, name, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerListJobResultsSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerListJobResultsQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerListJobResults>>> = ({
    signal,
  }) => safeSynthesizerListJobResults(workspace, name, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerListJobResultsSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerListJobResults>>
>;
export type SafeSynthesizerListJobResultsSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerListJobResultsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerListJobResultsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerListJobResultsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
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

export function useSafeSynthesizerListJobResultsSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerListJobResults>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerListJobResultsSuspenseQueryOptions(
    workspace,
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
 * @summary Get Job Status
 */
export const safeSynthesizerGetJobStatus = (
  workspace: string,
  name: string,
  signal?: AbortSignal
) => {
  return customFetch<PlatformJobStatusResponse>({
    url: `/apis/safe-synthesizer/v2/workspaces/${encodeURIComponent(String(workspace))}/jobs/${encodeURIComponent(String(name))}/status`,
    method: 'GET',
    signal,
  });
};

export const getSafeSynthesizerGetJobStatusQueryKey = (workspace: string, name: string) => {
  return [`/apis/safe-synthesizer/v2/workspaces/${workspace}/jobs/${name}/status`] as const;
};

export const getSafeSynthesizerGetJobStatusQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>, TError, TData>
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerGetJobStatusQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>> = ({
    signal,
  }) => safeSynthesizerGetJobStatus(workspace, name, signal);

  return { queryKey, queryFn, enabled: !!(workspace && name), ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerGetJobStatusQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>
>;
export type SafeSynthesizerGetJobStatusQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerGetJobStatus<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>, TError, TData>
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): DefinedUseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobStatus<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>, TError, TData>
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
          TError,
          Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>
        >,
        'initialData'
      >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobStatus<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Status
 */

export function useSafeSynthesizerGetJobStatus<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseQueryOptions<Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>, TError, TData>
    >;
  },
  queryClient?: QueryClient
): UseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerGetJobStatusQueryOptions(workspace, name, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<TData, TError> & {
    queryKey: DataTag<QueryKey, TData, TError>;
  };

  return { ...query, queryKey: queryOptions.queryKey };
}

export const getSafeSynthesizerGetJobStatusSuspenseQueryOptions = <
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
        TError,
        TData
      >
    >;
  }
) => {
  const { query: queryOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getSafeSynthesizerGetJobStatusQueryKey(workspace, name);

  const queryFn: QueryFunction<Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>> = ({
    signal,
  }) => safeSynthesizerGetJobStatus(workspace, name, signal);

  return { queryKey, queryFn, ...queryOptions } as UseSuspenseQueryOptions<
    Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type SafeSynthesizerGetJobStatusSuspenseQueryResult = NonNullable<
  Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>
>;
export type SafeSynthesizerGetJobStatusSuspenseQueryError = ErrorType<HTTPValidationError>;

export function useSafeSynthesizerGetJobStatusSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options: {
    query: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobStatusSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
export function useSafeSynthesizerGetJobStatusSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> };
/**
 * @summary Get Job Status
 */

export function useSafeSynthesizerGetJobStatusSuspense<
  TData = Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
  TError = ErrorType<HTTPValidationError>,
>(
  workspace: string,
  name: string,
  options?: {
    query?: Partial<
      UseSuspenseQueryOptions<
        Awaited<ReturnType<typeof safeSynthesizerGetJobStatus>>,
        TError,
        TData
      >
    >;
  },
  queryClient?: QueryClient
): UseSuspenseQueryResult<TData, TError> & { queryKey: DataTag<QueryKey, TData, TError> } {
  const queryOptions = getSafeSynthesizerGetJobStatusSuspenseQueryOptions(workspace, name, options);

  const query = useSuspenseQuery(queryOptions, queryClient) as UseSuspenseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  return { ...query, queryKey: queryOptions.queryKey };
}
