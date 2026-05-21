// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEffect } from 'react';
import { type FieldValues, type Path, useFormContext } from 'react-hook-form';

/**
 * Hook to set a react-hook-form field error on an API error. It's nice to keep field errors
 * entirely in react-hook-form so you don't have to mix together regular form errors and API errors
 * manually in the field components.
 *
 * @param fieldName - The name of the field to set the error on
 * @param error - The error to set on the field
 */
export const useSetFieldErrorOnApiError = <TFieldValues extends FieldValues = FieldValues>(
  fieldName: Path<TFieldValues>,
  error?: Error | null
) => {
  const { setError, clearErrors } = useFormContext<TFieldValues>();

  useEffect(() => {
    if (error) {
      setError(fieldName, { message: error.message });
    } else {
      clearErrors(fieldName);
    }
  }, [error, fieldName, setError, clearErrors]);
};
