// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DEFAULT_WORKSPACE } from '@nemo/common/src/models/constants';
import { filesDownloadFile, filesUploadFile } from '@nemo/sdk/generated/platform/api';
import axios from 'axios';

export interface LargeFileWorkerMessage {
  dataset: string;
  workspace?: string;
  file?: File;
  action: 'download' | 'downloadAsFile' | 'upload';
  path?: string;
  url?: string;
  /** Access token passed from the main thread (localStorage is unavailable in workers). */
  accessToken?: string;
}

/**
 * This worker is used to download/upload large files from the server.
 * It sends progress updates to the main thread.
 */
self.onmessage = async function (e: MessageEvent<LargeFileWorkerMessage>) {
  const { dataset, workspace, file, action, url, path, accessToken } = e.data;

  if (accessToken) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
  }

  switch (action) {
    case 'download': {
      if (!url) {
        self.postMessage({ done: true, error: 'URL is required' });
        break;
      }
      try {
        const response = await fetch(url);
        const reader = response.body?.getReader();
        const contentLength = +response.headers.get('Content-Length')!;
        let receivedLength = 0;
        const chunks = [];

        while (true) {
          const { done, value } = await reader!.read();
          if (done) break;

          chunks.push(value);
          receivedLength += value.length;

          const progress = Math.floor((receivedLength / contentLength) * 100);
          self.postMessage({ progress });
        }

        const text = chunks.map((chunk: Uint8Array) => new TextDecoder().decode(chunk)).join('');
        self.postMessage({ done: true, text });
      } catch (error) {
        self.postMessage({ done: true, error: String(error) });
      }
      break;
    }
    case 'downloadAsFile': {
      if (!path) {
        self.postMessage({ done: true, error: 'Path is required' });
        break;
      }
      try {
        const response = await filesDownloadFile(workspace || DEFAULT_WORKSPACE, dataset, path);
        const arrayBuffer = await response.arrayBuffer();
        self.postMessage({ done: true, arrayBuffer }, { transfer: [arrayBuffer] });
      } catch (error) {
        self.postMessage({ done: true, error: String(error) });
      }
      break;
    }
    case 'upload': {
      if (!file) {
        self.postMessage({ done: true, error: 'File is required' });
        break;
      }
      try {
        const blob = new Blob([await file.arrayBuffer()], {
          type: file.type || 'application/octet-stream',
        });
        await filesUploadFile(workspace || DEFAULT_WORKSPACE, dataset, file.name, blob);
        self.postMessage({ done: true });
      } catch (error) {
        self.postMessage({ done: true, error: String(error) });
      }
      break;
    }
    default:
      self.postMessage({ done: true, error: `Invalid action: ${action}` });
  }
};
