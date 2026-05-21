// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export default {
  // Code files - lint and format
  '**/*.{js,jsx,ts,tsx}': (files) => [
    `eslint --fix --no-warn-ignored --max-warnings 0 ${files.join(' ')}`,
    `prettier --write ${files.join(' ')}`,
  ],

  // Non-code files - format only
  '**/*.{json,yaml,yml,md}': (files) => `prettier --write ${files.join(' ')}`,
};
