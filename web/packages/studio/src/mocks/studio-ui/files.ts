// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { mockDateTool } from '@studio/mocks/studio-ui/tool';

export const mockFile = new File(['file-content'], 'test-file.txt', {
  type: 'text/plain',
});

export const mockFile2 = new File(['another-content'], 'test-file2.txt', {
  type: 'text/plain',
});

export const mockFile3 = new File(['image-content'], 'test-image.jpg', {
  type: 'image/jpeg',
});

export const mockFileJson = new File(['{"key":"value"}'], 'test-json.json', {
  type: 'text/json',
});

export const mockToolsFileJson = new File([JSON.stringify(mockDateTool)], 'test-tools.json', {
  type: 'text/json',
});
