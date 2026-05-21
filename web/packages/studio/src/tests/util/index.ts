// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MockStudioDataView } from '@studio/tests/util/mockStudioDataView';

export const studioDataViewMock = () => ({
  StudioDataView: MockStudioDataView,
  StudioDataViewToolbar: () => null,
  ROW_SELECTION_COLUMN_SIZE: 50,
  ROW_ACTIONS_COLUMN_SIZE: 50,
});
