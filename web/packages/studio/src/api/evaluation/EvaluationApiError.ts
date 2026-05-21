// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ErrorResponse, HTTPValidationError } from '@nemo/sdk/generated/platform/schema';

const isHttpValidationError = (
  response: HTTPValidationError | ErrorResponse
): response is HTTPValidationError => {
  return 'detail' in response && Array.isArray(response.detail);
};

export class EvaluationApiError extends Error {
  constructor(public response: ErrorResponse | HTTPValidationError) {
    let message;
    if (isHttpValidationError(response)) {
      message = response.detail?.map((err: { msg?: string }) => err.msg).join('');
    } else {
      // ErrorResponse has {detail: string}
      message = response.detail;
    }

    super(message || 'Unknown error');
  }
}
