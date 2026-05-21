// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import openApiFetchCreateClient, { ClientOptions } from 'openapi-fetch';

/**
 * This hack exists because the default value for openapi-fetch's `createClient`'s
 * `fetch` arg is incompatible with MSW 2.0. If our openapi-fetch based clients don't
 * override `fetch` like below, then MSW 2.0 isn't able to intercept any requests in tests.
 *
 * This is simply a wrapper to DRY up this hack.
 *
 * https://github.com/mswjs/msw/issues/2180
 */
export const createClient = <Paths extends NonNullable<unknown>>(
  clientOptions: Omit<ClientOptions, 'fetch'>
) => {
  return openApiFetchCreateClient<Paths>({
    ...clientOptions,
    fetch: (input, init) => fetch(input, init),
  });
};
