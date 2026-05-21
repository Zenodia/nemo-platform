// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DEMO_DATASET, type SetupFn } from '@screenshots/config';

export const setupDatasets: SetupFn = async (page) => {
  // Wait for file table to load
  const row = page.locator('tr', { hasText: 'evaluation.jsonl' }).first();

  // Click the "..." action menu
  const menuTrigger = row.getByTestId('quick-actions-menu-trigger');
  await menuTrigger.waitFor({ timeout: 3_000 });
  await menuTrigger.click();

  // Wait for menu to fully render, then let animation complete
  await page.getByText('View File').waitFor({ timeout: 5000 });
  await page.waitForTimeout(500);
};

export const setupSafeSynthesizer: SetupFn = async (page) => {
  // 1. Click "Select File" button
  await page.getByRole('button', { name: 'Select File' }).click();

  // 2. Wait for modal to open
  await page.getByRole('heading', { name: 'Select a File' }).waitFor({ timeout: 5_000 });

  // 3. Open the fileset dropdown and pick the demo dataset
  await page.getByTestId('nv-select-trigger').click();
  await page.getByRole('option', { name: DEMO_DATASET }).click();

  // 4. Wait for file list to appear, then check "training.jsonl"
  await page.getByText('training.jsonl').waitFor({ timeout: 5_000 });
  const trainingRow = page.locator('tr', { hasText: 'training.jsonl' });
  await trainingRow.getByTestId('nv-checkbox-box').click();

  // 5. Click "Add Selected File"
  await page.getByRole('button', { name: 'Add Selected File' }).click();

  // 6. Wait for modal to close
  await page.getByRole('heading', { name: 'Select a File' }).waitFor({
    state: 'hidden',
    timeout: 10_000,
  });

  // 7. Wait for modal overlay dismiss animation to complete
  await page.waitForTimeout(500);
};

export const setupWorkspaces: SetupFn = async (page) => {
  // 1. Open the workspace dropdown in the breadcrumb
  await page.getByRole('button', { name: 'Select workspace' }).click();
  await page.waitForTimeout(500);

  // 2. Click "+ New Workspace" at the bottom of the dropdown
  await page.getByText('New Workspace').click();

  // 3. Wait for the create modal to appear
  await page.getByRole('dialog').waitFor({ state: 'visible', timeout: 5_000 });
  await page.waitForTimeout(500);

  // 4. Fill in the form fields (KUI shares id between input and wrapper div,
  //    so we target the actual input/textarea elements by test ID)
  await page.getByTestId('nv-text-input-element').fill('demo');
  await page.getByTestId('nv-text-area-element').fill('Getting started with Studio');
};
