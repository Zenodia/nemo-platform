// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { MessageStatus } from '@assistant-ui/react';

export const RUNNING_STATUS: MessageStatus = { type: 'running' };
export const COMPLETE_STATUS: MessageStatus = { type: 'complete', reason: 'stop' };
export const CANCELLED_STATUS: MessageStatus = { type: 'incomplete', reason: 'cancelled' };
