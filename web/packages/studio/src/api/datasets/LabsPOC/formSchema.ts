// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Form schema types for LabsPOC useSplitDataset.
 * Split percentages (0-100) for eval, train, validation, icls.
 */
export interface SplitFormData {
  eval: number;
  train: number;
  validate: number;
  icls: number;
}
