// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import axios from 'axios';
import type { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import qs from 'qs';
import { User } from 'oidc-client-ts';
import { resolveBrowserBaseUrl } from '../../src/utils/url';

const headers = {
  'X-Source': 'NeMo Studio',
};

interface RequestOptions extends AxiosRequestConfig {
  params?: Record<string, string | number | boolean | object | unknown>;
}

// Add X-Source header and OIDC Bearer token to ALL requests
axios.interceptors.request.use((config) => {
  Object.assign(config.headers, headers);

  // If Authorization is already set (e.g. via axios.defaults in a Web Worker), skip OIDC lookup
  if (config.headers.Authorization) {
    return config;
  }

  // Attach OIDC access token as Bearer token if available
  // Guard localStorage access — it is unavailable in Web Worker contexts
  const authority = import.meta.env.VITE_AUTH_AUTHORITY;
  const clientId = import.meta.env.VITE_AUTH_CLIENT_ID;
  if (authority && clientId && typeof localStorage !== 'undefined') {
    const oidcStorageKey = `oidc.user:${authority}:${clientId}`;
    const oidcStorage = localStorage.getItem(oidcStorageKey);
    if (oidcStorage) {
      try {
        const user = User.fromStorageString(oidcStorage);
        if (user?.access_token && !user.expired) {
          config.headers.Authorization = `Bearer ${user.access_token}`;
        }
      } catch {
        // Remove malformed storage entry and trigger re-authentication
        console.warn(
          'Malformed OIDC storage entry detected. Clearing storage and re-authenticating.'
        );
        localStorage.removeItem(oidcStorageKey);
      }
    }
  }

  return config;
});

const getBaseUrl = (): string | undefined => {
  // Check Vite environment variables first (import.meta.env)
  const VITE_VALUE_VITE_PLATFORM_BASE_URL = import.meta.env.VITE_PLATFORM_BASE_URL;
  if (VITE_VALUE_VITE_PLATFORM_BASE_URL && VITE_VALUE_VITE_PLATFORM_BASE_URL.trim() !== '') {
    return resolveBrowserBaseUrl(VITE_VALUE_VITE_PLATFORM_BASE_URL);
  }

  // Fallback to Node.js process.env
  if (typeof process !== 'undefined' && process.env) {
    const NODE_VALUE_PLATFORM_BASE_URL = process.env.PLATFORM_BASE_URL;
    if (NODE_VALUE_PLATFORM_BASE_URL && NODE_VALUE_PLATFORM_BASE_URL.trim() !== '') {
      return NODE_VALUE_PLATFORM_BASE_URL;
    }
  }

  // If no variables found, return empty string
  return '';
};

const getUrl = (request: AxiosRequestConfig): string => {
  const baseUrl = getBaseUrl();
  const { url } = request;
  const fullUrl = `${baseUrl}${url}`;

  if (!baseUrl) {
    return fullUrl;
  }

  try {
    // Construct the full URL with base URL and query parameters
    return new URL(fullUrl).toString();
  } catch (error) {
    console.error('Invalid URL:', fullUrl, error);
    throw new Error(`Invalid URL format: ${fullUrl}`);
  }
};

export const customFetch = async <TData>(request: RequestOptions): Promise<TData> => {
  const requestUrl = getUrl(request);
  const response: AxiosResponse<TData> = await axios({
    ...request,
    url: requestUrl,
    paramsSerializer: {
      serialize: (params) => qs.stringify(params, { indices: false }),
    },
  });
  return response.data;
};

// https://orval.dev/reference/configuration/output#mutator
// In some case with react-query and swr you want to be able to override the return error type so you can also do it here like this
export type ErrorType<TError> = AxiosError<TError>;
