// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * @deprecated This type is no longer needed with v2 fileset APIs.
 * Use standard File or Blob objects directly with filesUploadFile().
 */
export type FileContentsWithPath = { path: string; content: Blob | string };
