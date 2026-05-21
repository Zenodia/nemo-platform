// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/*
 * This file contains a function, `fetchWithCSRF` which is a simple wrapper for `window.fetch` that adds
 * in a CSRF header containing the last received CSRF token from a GET request. It simply contains this
 * state in a "global" variable. It also exports other functions for managing this token state.
 */

export const CSRF_HEADER_NAME = 'x-csrf-token';

let lastCsrfToken: string = '';

const BASE_REQUEST: RequestInit = {
  redirect: 'follow',
  mode: 'cors',
  credentials: 'include',
};

export function initGetRequest(): RequestInit {
  return {
    ...BASE_REQUEST,
    method: 'GET',
  };
}

export function initPostRequest(): RequestInit {
  return {
    ...BASE_REQUEST,
    method: 'POST',
  };
}

/**
 * Gets the last stored CSRF token
 *
 * @returns the last stored CSRF token
 */
export function getLastCsrfToken() {
  return lastCsrfToken;
}

/**
 * Stores a new CSRF token to use in subsequent fetches
 *
 * @param token the token to use
 */
export function setLastCsrfToken(token: string) {
  lastCsrfToken = token;
}

/**
 * Adds a CSRF header to the provided header with the last known CSRF token value
 *
 * @param headers the headers to add the CSRF header to
 * @returns
 */
export function addCsrfToRequestHeaders(headers?: HeadersInit): HeadersInit {
  return {
    ...headers,
    [CSRF_HEADER_NAME]: lastCsrfToken,
  };
}

/**
 * Extracts the value of the CSRF token from a CSRF header.
 *
 * @param responseHeaders the headers object to extract from
 */
export function extractCsrfFromResponseHeaders(responseHeaders?: Headers) {
  const value = responseHeaders?.get(CSRF_HEADER_NAME);
  if (typeof value === 'string' && !!value) {
    setLastCsrfToken(value);
  }
}

/**
 * Adds app-required CSRF token extract-send functionality to the original fetch.
 *
 * @param resource the resource to fetch
 * @param options optional request options
 * @returns a promise that resolves with a Response
 */
export async function fetchWithCsrf(
  resource: RequestInfo | URL,
  options?: RequestInit | undefined
): Promise<Response> {
  const defaultOptions = initGetRequest();
  const mergedOptions: RequestInit = { ...defaultOptions, ...options };
  mergedOptions.headers = addCsrfToRequestHeaders(mergedOptions?.headers);

  const response: Response = await fetch(resource, mergedOptions);
  extractCsrfFromResponseHeaders(response.headers);
  return response;
}
