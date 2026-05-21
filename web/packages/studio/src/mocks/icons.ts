// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { http, HttpResponse } from 'msw';

const mockSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <path d="M12 6v6l4 2"/>
</svg>`;

export const handlers = [
  http.get(
    `https://brand-assets.cne.ngc.nvidia.com/assets/icons/*`,
    async () =>
      new HttpResponse(mockSvg, {
        headers: {
          'Content-Type': 'image/svg+xml',
        },
      })
  ),
];
