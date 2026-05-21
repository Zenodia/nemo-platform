// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { create } from 'zustand';

interface DetailsChartsState {
  selectedEvaluations: string[];
  setSelectedEvaluations: (ids: string[]) => void;
}

export const useDetailsChartsStore = create<DetailsChartsState>((set) => ({
  selectedEvaluations: [],
  setSelectedEvaluations: (ids) => set({ selectedEvaluations: ids }),
}));
