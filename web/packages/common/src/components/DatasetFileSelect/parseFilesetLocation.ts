// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Resolved location for calling Files service fileset endpoints from a job `artifact_url`.
 * Matches `parse_fileset_ref` in the Python SDK (hash form, legacy slashes, optional `fileset://`).
 */
export interface ParsedFilesetArtifactUrl {
  workspace: string;
  name: string;
  /**
   * Path inside the fileset (object key), if any; empty when the ref is only workspace/fileset.
   */
  objectPath: string;
  /**
   * Optional `path` query param for `filesListFilesetFiles` (path prefix filter).
   */
  filesListPathPrefix?: string;
}

/**
 * Directory prefix for listing files under an artifact path inside the fileset.
 */
export const listPathPrefixFromObjectPath = (pathInFileset: string): string | undefined => {
  const trimmed = pathInFileset.replace(/\/+$/, '');
  if (!trimmed) {
    return undefined;
  }
  const lastSlash = trimmed.lastIndexOf('/');
  if (lastSlash === -1) {
    return trimmed.includes('.') ? undefined : trimmed;
  }
  const lastSegment = trimmed.slice(lastSlash + 1);
  return lastSegment.includes('.') ? trimmed.slice(0, lastSlash) : trimmed;
};

/**
 * Parses a fileset reference into workspace, fileset name, optional object path, and optional list-files path prefix.
 *
 * Supported shapes (same as Python `parse_fileset_ref`):
 * - `fileset://workspace/fileset` or `fileset://workspace/fileset#path`
 * - `workspace/fileset#path` or `fileset#path` (use `workspaceFallback` when workspace omitted)
 * - `workspace/fileset` (root)
 * - Legacy: `workspace/fileset/path/inside/...` (3+ slash segments, no `#`)
 *
 * @param workspaceFallback - Route/workspace context when the ref omits workspace (e.g. `my-fs#data.txt`).
 */
export function parseFilesetLocation(
  url: string,
  workspaceFallback?: string
): ParsedFilesetArtifactUrl | null {
  let ref = url.trim();
  if (ref.startsWith('fileset://')) {
    ref = ref.slice('fileset://'.length);
  }
  ref = ref.replace(/^\//, '');
  if (!ref) {
    return null;
  }

  let workspace = '';
  let fileset = '';
  let filePath = '';

  const hashIdx = ref.indexOf('#');
  if (hashIdx !== -1) {
    const filesetPart = ref.slice(0, hashIdx);
    filePath = ref.slice(hashIdx + 1).replace(/^\/+/, '');
    const slashInPart = filesetPart.lastIndexOf('/');
    if (slashInPart !== -1) {
      workspace = filesetPart.slice(0, slashInPart);
      fileset = filesetPart.slice(slashInPart + 1);
    } else {
      fileset = filesetPart;
    }
  } else {
    const parts = ref.split('/').filter(Boolean);
    if (parts.length === 1) {
      fileset = parts[0]!;
    } else if (parts.length === 2) {
      workspace = parts[0]!;
      fileset = parts[1]!;
    } else if (parts.length >= 3) {
      workspace = parts[0]!;
      fileset = parts[1]!;
      filePath = parts.slice(2).join('/');
    }
  }

  if (!fileset) {
    return null;
  }
  if (!workspace && workspaceFallback) {
    workspace = workspaceFallback;
  }
  if (!workspace) {
    return null;
  }

  const filesListPathPrefix = listPathPrefixFromObjectPath(filePath);
  return { workspace, name: fileset, objectPath: filePath, filesListPathPrefix };
}
