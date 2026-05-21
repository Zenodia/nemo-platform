// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * One entry in the shared "models we are comparing" list owned by ModelCompareRoute.
 * Children (Chat, Prompts) render based on this list but keep their own per-entry
 * ephemeral state (collapsed, chat history, response cells, etc.) keyed by id.
 */
export interface SharedModelEntry {
  id: number;
  /** Full URN, e.g. "abacusai/dracarys-llama-70b". Null means unassigned. */
  modelURN: string | null;
}

/** Shape consumed by ModelChatPanel — composed per-render from shared entry + local state. */
export interface PanelState {
  id: number;
  collapsed: boolean;
  /** Full model URN ("workspace/name"), or null if unassigned. */
  modelURN: string | null;
}
