// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Default number of input records to sample when automatic sampling is disabled.
 * This value is used as a fallback when the user unchecks "Use Automatic Sampling".
 */
export const DEFAULT_NUM_INPUT_RECORDS_TO_SAMPLE = 25000;

/**
 * Maximum number of records that can be processed or sampled.
 * This limit ensures performance and memory constraints are respected.
 */
export const MAX_NUM_RECORDS = 130_000;
