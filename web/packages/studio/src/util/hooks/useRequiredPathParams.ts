// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useParams } from 'react-router';

/**
 * Returns an object containing the path params provided by paramsList, or throws if they can't
 * be found.
 *
 * Example:
 * ```
 * const { projectNamespace, projectName } = useRequiredPathParams([ROUTE_PARAMS.projectNamespace, ROUTE_PARAMS.projectName]);
 * ```
 *
 * @throws if missing any params not in the params list
 */
export const useRequiredPathParams = <T extends string>(paramsList: T[]): Record<T, string> => {
  const params = useParams();

  const missingParams = paramsList.filter((param) => !(param in params));

  if (missingParams.length > 0) {
    throw new Error(`Missing required parameters: ${missingParams.join(', ')}`);
  }
  // Subset of params to match passed paramsList
  const validatedParams: Record<T, string> = {} as Record<T, string>;
  paramsList.forEach((param) => {
    validatedParams[param] = params[param]!;
  });

  return validatedParams;
};
