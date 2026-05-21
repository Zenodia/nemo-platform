// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export const FEEDBACK_CATEGORY_KEY = 'studio_feedback';
export const FEEDBACK_CATEGORIES = [
  'Too much information',
  'Not enough information',
  'Not factually correct',
  "Didn't fully follow instructions",
];

export enum FeedbackAddToDatasetFileSource {
  New = 'Create new',
  Existing = 'Add to existing',
}
