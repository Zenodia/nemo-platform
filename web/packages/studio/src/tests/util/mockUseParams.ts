// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import * as router from 'react-router';
import type { Mock } from 'vitest';

export const mockUseParams = (params?: router.Params) => {
  vitest.spyOn(router, 'useParams').mockImplementation(() => {
    return params ?? {};
  });
};

export const mockUseNavigate = (mockImplementation?: Mock) => {
  vitest.spyOn(router, 'useNavigate').mockImplementation(() => {
    return mockImplementation ?? vi.fn();
  });
};
