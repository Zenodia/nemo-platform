// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// Training / Testing / Validation
const SELECT_SPLIT_PERCENTAGES = [
  [80, 10, 10],
  [60, 20, 20],
  [80, 20],
  [90, 10],
];

export const splitDescriptorToList = {
  '80% Training, 10% Testing, 10% Validation (Recommended)': SELECT_SPLIT_PERCENTAGES[0].map(
    (percentage) => `${percentage}%`
  ),
  '60% Training, 20% Testing, 20% Validation': SELECT_SPLIT_PERCENTAGES[1].map(
    (percentage) => `${percentage}%`
  ),
  '80% Training, 20% Testing': SELECT_SPLIT_PERCENTAGES[2].map((percentage) => `${percentage}%`),
  '90% Training, 10% Testing': SELECT_SPLIT_PERCENTAGES[3].map((percentage) => `${percentage}%`),
};

export const SELECT_SPLIT_OPTIONS = SELECT_SPLIT_PERCENTAGES.map((percentages, groupIndex) => {
  const isRecommended = groupIndex === 0;

  return (
    percentages
      .map((percentage, splitIndex) => {
        if (splitIndex === 0) {
          return `${percentage}% Training`;
        }
        if (splitIndex === 1) {
          return `${percentage}% Testing`;
        }
        return `${percentage}% Validation`;
      })
      .join(', ') + (isRecommended ? ' (Recommended)' : '')
  );
}).concat(['Custom Percentage']);
