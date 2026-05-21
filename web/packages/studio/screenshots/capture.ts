// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/* eslint-disable no-console -- CLI script: console is the correct output mechanism */
import { chromium } from '@playwright/test';
import { defaultViewport, privacyReplacements, screenshots } from '@screenshots/config';
import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';
import { loadEnv } from 'vite';

// Load Vite env files (mode defaults to 'dev' locally; CI can override via NODE_ENV)
const envDir = path.resolve(import.meta.dirname, '../env');
const viteEnv = loadEnv(process.env.NODE_ENV || 'dev', envDir);
Object.assign(process.env, viteEnv);

/** When true, routes are rewritten to strip the /studio prefix (local dev serves at /) */
const localMode = process.argv.includes('--local');

function resolveStudioUrl(): string {
  if (process.env.STUDIO_URL) {
    return process.env.STUDIO_URL;
  }
  if (localMode) {
    return 'http://localhost:5173/';
  }
  if (process.env.VITE_PLATFORM_BASE_URL) {
    const base = process.env.VITE_PLATFORM_BASE_URL.replace(/\/+$/, '');
    return `${base}/studio/`;
  }
  throw new Error(
    'Could not determine Studio URL. Use one of:\n\n' +
      '  VITE_PLATFORM_BASE_URL  Set in your .env.dev.local\n' +
      '  STUDIO_URL=<url>        Override via environment variable\n' +
      '  --local                 Target the local dev server'
  );
}

/** Strip the /studio prefix from a route when running in local dev mode */
function resolveRoute(route: string): string {
  if (localMode) {
    return route.replace(/^\/studio/, '');
  }
  return route;
}

const OUTPUT_DIR = path.resolve(import.meta.dirname, '../../../../docs/studio/_images');

/** CSS to hide the TanStack React Query devtools panel toggle */
const HIDE_DEVTOOLS_CSS = `
  .tsqd-open-btn-container,
  .tsqd-parent-container,
  [class*="ReactQueryDevtools"] {
    display: none !important;
  }
`;

function waitForEnter(prompt: string): Promise<void> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(prompt, () => {
      rl.close();
      resolve();
    });
  });
}

async function main() {
  const STUDIO_URL = resolveStudioUrl();

  if (screenshots.length === 0) {
    console.log('No screenshots configured in config.ts — nothing to capture.');
    return;
  }

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: defaultViewport,
  });
  const page = await context.newPage();

  // Navigate to the base URL so the user can log in
  await page.goto(STUDIO_URL);

  await waitForEnter('\nLog in and prepare the app, then press Enter to continue...\n');

  // Dismiss the "Welcome to NeMo Studio" tour modal if it appears
  const skipBtn = page.getByRole('button', { name: 'Skip' });
  if (await skipBtn.isVisible({ timeout: 3_000 }).catch(() => false)) {
    await skipBtn.click();
    console.log('Dismissed welcome tour modal');
  }

  // Switch to light mode if currently in dark mode
  const lightModeToggle = page.getByRole('button', { name: 'Switch to light theme' });
  if (await lightModeToggle.isVisible().catch(() => false)) {
    await lightModeToggle.click();
    console.log('Switched to light mode');
  }

  // Inject CSS to suppress React Query devtools across all navigations
  await context.addInitScript(() => {
    const style = document.createElement('style');
    style.textContent = `
      .tsqd-open-btn-container,
      .tsqd-parent-container,
      [class*="ReactQueryDevtools"] {
        display: none !important;
      }
    `;
    document.head.appendChild(style);
  });

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  for (const entry of screenshots) {
    const url = new URL(resolveRoute(entry.route), STUDIO_URL).href;
    console.log(`Capturing "${entry.name}" → ${url}`);

    // Apply per-screenshot viewport if specified
    if (entry.viewport) {
      await page.setViewportSize(entry.viewport);
    } else {
      await page.setViewportSize(defaultViewport);
    }

    await page.goto(url, { waitUntil: 'networkidle' });

    // Re-inject the hide CSS on each page load (SPA navigations keep it, full loads don't)
    await page.addStyleTag({ content: HIDE_DEVTOOLS_CSS });

    if (entry.waitFor) {
      await page.waitForSelector(entry.waitFor, { timeout: 15_000 });
    }

    if (entry.delay) {
      await page.waitForTimeout(entry.delay);
    }

    // Apply privacy replacements before setup — modifying text nodes after
    // setup could close menus/popups by triggering React re-renders
    const replacementEntries = Object.entries(privacyReplacements);
    if (replacementEntries.length > 0) {
      await page.evaluate((replacements) => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node: Text | null;
        while ((node = walker.nextNode() as Text | null)) {
          let text = node.nodeValue ?? '';
          for (const [original, replacement] of replacements) {
            text = text.replaceAll(original, replacement);
          }
          node.nodeValue = text;
        }
      }, replacementEntries);
    }

    // Run per-screenshot setup automation (click buttons, fill forms, etc.)
    if (entry.setup) {
      await entry.setup(page);
    }

    const outputPath = path.join(OUTPUT_DIR, `${entry.name}.png`);
    await page.screenshot({
      path: outputPath,
      clip: entry.clip,
    });

    console.log(`  ✓ Saved ${outputPath}`);
  }

  await browser.close();
  console.log(`\nDone — captured ${screenshots.length} screenshot(s).`);
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
