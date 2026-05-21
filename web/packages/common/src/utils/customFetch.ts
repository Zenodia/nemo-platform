// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Custom Fetch Function for MSW Compatibility
 * -------------------------------------------
 *
 * We use this custom `fetch` function to ensure compatibility with `msw` (Mock Service Worker) version 2.0 during
 * testing, while leveraging the built-in `fetch` available in Node.js 18 and above for production use.
 *
 * Background:
 * - **`openapi-fetch`:** A library that generates API clients based on OpenAPI specifications. By default, it uses its
 * own `fetch` implementation.
 * - **`msw` 2.0 Issue:** `msw` is a library for mocking network requests in tests by intercepting `fetch` calls. In
 * version 2.0, `msw` introduced changes that made it incompatible with custom `fetch` implementations like the one used by `openapi-fetch`. Specifically, `msw` 2.0 expects the global `fetch` function to be the standard Fetch API.
 * - **Node.js Built-in `fetch`:** Starting from Node.js 18, a native implementation of the Fetch API is available
 * globally, matching the standard used in browsers.
 *
 * **Why This Custom `fetch` Function Is Necessary:**
 * - **Testing Compatibility:** To allow `msw` to intercept HTTP requests during tests, we need to ensure that the
 * `fetch` function used by `openapi-fetch` is compatible with `msw` 2.0.
 * - **Standard Compliance:** By using the built-in `fetch` from Node.js, we ensure that our `fetch` implementation
 * adheres to the standard Fetch API, which `msw` expects.
 * - **Avoiding Custom Clients in Production:** Instead of creating a custom `createClient` function for
 * `openapi-fetch`, which can introduce complexity and potential bugs in production, we override the `fetch` function
 * only. This makes our production code cleaner and more maintainable.
 *
 * **How It Works:**
 * - **In Production:**
 *   - The custom `fetch` function simply calls the built-in `fetch` provided by Node.js.
 *   - This ensures that all network requests behave as expected in a production environment.
 * - **In Testing:**
 *   - `msw` intercepts calls to the standard `fetch` function.
 *   - By using the built-in `fetch`, we allow `msw` to mock network requests effectively during tests.
 * - **No Additional Dependencies:** Since Node.js 18+ includes `fetch` natively, we don't need external libraries
 * like `node-fetch` or `cross-fetch`, reducing our dependency footprint.
 *
 * **Related Issues and References:**
 * - **`msw` Compatibility Issue:** The incompatibility between `msw` 2.0 and custom `fetch` implementations is
 * discussed in the `msw` GitHub repository: https://github.com/mswjs/msw/issues/2180
 * - **Node.js `fetch` Documentation:** For more details on the built-in `fetch` in Node.js, see the official
 * documentation: https://nodejs.org/api/globals.html#fetch
 *
 * // client.ts
 *
 * import { createClient } from 'openapi-fetch';
 * import { customFetch } from './customFetch';
 *
 * export const client = createClient<Paths>({
 *   baseUrl: 'https://your-api.com',
 *   fetch: customFetch,
 *   // Other options
 * });
 * ```
 */
export const customFetch = async (input: RequestInfo, init?: RequestInit): Promise<Response> => {
  return fetch(input, init);
};
