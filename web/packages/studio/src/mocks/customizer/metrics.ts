// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { CustomizationJob } from '@nemo/sdk/vendored/customizer/schema';

export const customizationMetrics1: CustomizationJob['status_details'] = {
  keys: ['train_loss', 'val_loss'],
  metrics: {
    train_loss: [
      {
        value: 0.15,
        step: 2,
        timestamp: '2024-06-25T21:53:42.416387Z',
      },
      {
        value: 0.35,
        step: 4,
        timestamp: '2024-06-25T21:54:42.416387Z',
      },
      {
        value: 0.55,
        step: 6,
        timestamp: '2024-06-25T21:55:42.416387Z',
      },
      {
        value: 0.85,
        step: 8,
        timestamp: '2024-06-25T21:56:42.416387Z',
      },
      {
        value: 0.9,
        step: 10,
        timestamp: '2024-06-25T21:57:42.416387Z',
      },
    ],
    val_loss: [
      {
        value: 0.5,
        step: 2,
        timestamp: '2024-06-25T21:53:42.416387Z',
      },
      {
        value: 0.6,
        step: 4,
        timestamp: '2024-06-25T21:54:42.416387Z',
      },
      {
        value: 0.7,
        step: 6,
        timestamp: '2024-06-25T21:55:42.416387Z',
      },
      {
        value: 0.8,
        step: 8,
        timestamp: '2024-06-25T21:56:42.416387Z',
      },
      {
        value: 0.9,
        step: 10,
        timestamp: '2024-06-25T21:57:42.416387Z',
      },
    ],
  },
};

export const customizationMetrics2: CustomizationJob['status_details'] = {
  keys: ['train_loss', 'val_loss'],
  metrics: {
    train_loss: [
      {
        value: 0.2,
        step: 10,
        timestamp: '2024-06-25T21:53:42.416387Z',
      },
      {
        value: 0.4,
        step: 20,
        timestamp: '2024-06-25T21:54:42.416387Z',
      },
      {
        value: 0.6,
        step: 30,
        timestamp: '2024-06-25T21:55:42.416387Z',
      },
      {
        value: 0.8,
        step: 40,
        timestamp: '2024-06-25T21:56:42.416387Z',
      },
      {
        value: 0.9,
        step: 50,
        timestamp: '2024-06-25T21:57:42.416387Z',
      },
    ],
    val_loss: [
      {
        value: 0.1,
        step: 10,
        timestamp: '2024-06-25T21:53:42.416387Z',
      },
      {
        value: 0.15,
        step: 20,
        timestamp: '2024-06-25T21:54:42.416387Z',
      },
      {
        value: 0.2,
        step: 30,
        timestamp: '2024-06-25T21:55:42.416387Z',
      },
      {
        value: 0.25,
        step: 40,
        timestamp: '2024-06-25T21:56:42.416387Z',
      },
      {
        value: 0.3,
        step: 50,
        timestamp: '2024-06-25T21:57:42.416387Z',
      },
    ],
  },
};

export const customizationMetrics3: CustomizationJob['status_details'] = {
  keys: ['train_loss', 'val_loss'],
  metrics: {
    train_loss: [
      {
        value: 0.01,
        step: 15,
        timestamp: '2024-06-25T21:53:42.416387Z',
      },
      {
        value: 0.05,
        step: 30,
        timestamp: '2024-06-25T21:54:42.416387Z',
      },
      {
        value: 0.1,
        step: 45,
        timestamp: '2024-06-25T21:55:42.416387Z',
      },
      {
        value: 0.5,
        step: 60,
        timestamp: '2024-06-25T21:56:42.416387Z',
      },
      {
        value: 0.99,
        step: 75,
        timestamp: '2024-06-25T21:57:42.416387Z',
      },
    ],
    val_loss: [
      {
        value: 0.9,
        step: 15,
        timestamp: '2024-06-25T21:53:42.416387Z',
      },
      {
        value: 0.8,
        step: 30,
        timestamp: '2024-06-25T21:54:42.416387Z',
      },
      {
        value: 0.5,
        step: 45,
        timestamp: '2024-06-25T21:55:42.416387Z',
      },
      {
        value: 0.2,
        step: 60,
        timestamp: '2024-06-25T21:56:42.416387Z',
      },
      {
        value: 0.01,
        step: 75,
        timestamp: '2024-06-25T21:57:42.416387Z',
      },
    ],
  },
};
