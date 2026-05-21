// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// Platform: Training options are part of hyperparameters, not a separate type
interface TrainingOption {
  training_type?: string;
  finetuning_type?: string;
}

// Helper function to get a human readable identifier for a given customizer training option set
export const getTrainingOptionsLabel = (options: TrainingOption) => {
  return `Training: ${options.training_type} | Finetuning: ${options.finetuning_type}`;
};
