// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { http, HttpResponse } from 'msw';

/**
 * Handlers for sample dataset static file requests.
 * These are fetched when the user selects the Sample Dataset tab (paths relative to BASE_URL).
 */
export const sampleDatasetsHandlers = [
  http.get(/\/sample-datasets\/qa-generation\/.*\.jsonl$/, () =>
    HttpResponse.text('{}', {
      headers: { 'Content-Type': 'application/jsonl' },
    })
  ),
];
