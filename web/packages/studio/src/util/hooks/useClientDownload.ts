// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useToast } from '@nemo/common/src/providers/toast/useToast';
import { triggerDownload } from '@nemo/common/src/utils/file';

/**
 * Take a file and download it as a file on the client.
 * Returns a function that can be used to download a file on the client.
 * @param file - The file to download.
 */
export const useClientDownload = () => {
  const toast = useToast();

  return (file: File) => {
    try {
      triggerDownload(file, file.name);
      toast.success('Successfully downloaded file!');
    } catch {
      toast.error('Unable to download file. Please try again later.');
    }
  };
};
