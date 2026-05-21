// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Shared mapping: @nv-brand-assets/react-icons-inline icon names -> lucide-react.
 * Used by scripts/migrate-icons.ts
 */

export const RENAME_MAP: Record<string, string> = {
  AccountCheck: 'UserCheck',
  Add: 'Plus',
  Apps: 'LayoutGrid',
  ArrowUp: 'ArrowUp',
  ArrowUpDown: 'ArrowUpDown',
  Cancel: 'Ban',
  Chart: 'ChartLine',
  ChatMessage: 'MessageSquare',
  ChatMulti: 'MessagesSquare',
  ChatNew: 'MessageSquarePlus',
  CheckCircle: 'CircleCheck',
  CheckmarkBadge: 'BadgeCheck',
  CheckMultiCircle: 'CircleCheckBig',
  ChevronDoubleDown: 'ChevronsDown',
  ChevronDoubleUp: 'ChevronsUp',
  ChevronDown: 'ChevronDown',
  ChevronUp: 'ChevronUp',
  CircleTick: 'CircleCheck',
  Close: 'X',
  CloseCircle: 'CircleX',
  CopyDoc: 'Copy',
  Cube: 'Box',
  CubeStack: 'Boxes',
  Db: 'Database',
  Document: 'File',
  DocumentCheckmark: 'FileCheck',
  DocumentNew: 'FilePlus',
  Download: 'Download',
  Error: 'CircleAlert',
  Export: 'Upload',
  Faders: 'SlidersHorizontal',
  Filter: 'Filter',
  Fork: 'GitFork',
  Generate: 'Sparkles',
  Head: 'Brain',
  HelpCircle: 'CircleHelp',
  InfoCircle: 'Info',
  LayoutRows: 'LayoutList',
  LockClosed: 'Lock',
  MagnifyingGlass: 'Search',
  MoreVert: 'EllipsisVertical',
  OpenExternal: 'ExternalLink',
  Paperplane: 'Send',
  Refresh: 'RefreshCw',
  Reset: 'RotateCcw',
  Running: 'Play',
  ScmBranch: 'GitBranch',
  Secure: 'ShieldCheck',
  Signature: 'PenLine',
  Sliders: 'SlidersHorizontal',
  SplitFile: 'Split',
  StackHorizontal: 'Layers',
  SunHigh: 'Sun',
  Sync: 'RefreshCw',
  Text: 'Type',
  TextAlignLeft: 'AlignLeft',
  ThumbDown: 'ThumbsDown',
  ThumbUp: 'ThumbsUp',
  Trash: 'Trash2',
  TrashDelete: 'Trash',
  Warning: 'TriangleAlert',
  Window: 'AppWindow',
  World: 'Globe',
  Stop: 'Square',
  TextFramed: 'FileText',
};

export const NO_MATCH_MAP: Record<string, string> = {
  GpuCardMulti: 'Circle',
};

export function getLucideName(imported: string): string {
  return NO_MATCH_MAP[imported] ?? RENAME_MAP[imported] ?? imported;
}
