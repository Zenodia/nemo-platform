// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/*
 * This module contains utility functions for parsing and converting dataset files.
 * It provides functions to parse file content based on its extension, convert data back to the appropriate format,
 * and get the MIME type for a given file extension.
 */

export type ParsedFileContent = Record<string, unknown>[];

export const SUPPORTED_FILE_EXTENSIONS = ['.json', '.jsonl'] as const;

export type SupportedFileExtension = (typeof SUPPORTED_FILE_EXTENSIONS)[number];

export const isSupportedDatasetFileExtension = (fileExtension?: string | null) => {
  return SUPPORTED_FILE_EXTENSIONS.includes(fileExtension as SupportedFileExtension);
};

export const parseFileContent = (
  text: string,
  fileExtension: SupportedFileExtension
): ParsedFileContent => {
  switch (fileExtension) {
    case '.json':
      return parseJsonFileContent(text);
    case '.jsonl':
      return parseJsonlFileContent(text);
    default:
      throw new Error(`Unsupported file type: ${fileExtension}`);
  }
};

export const convertToFileFormat = (
  data: ParsedFileContent,
  format: SupportedFileExtension
): string => {
  switch (format) {
    case '.json':
      return convertToJsonFormat(data);
    case '.jsonl':
      return convertToJsonlFormat(data);
    default:
      throw new Error(`Unsupported file type: ${format}`);
  }
};

export const getFileMimeType = (fileExtension: SupportedFileExtension) => {
  switch (fileExtension) {
    case '.json':
      return 'application/json';
    case '.jsonl':
      return 'application/jsonl';
    default:
      throw new Error(`Unsupported file type: ${fileExtension}`);
  }
};

export const parseJsonFileContent = (text: string): ParsedFileContent => {
  const jsonData = JSON.parse(text);
  if (!Array.isArray(jsonData)) {
    throw new Error('JSON file must contain a top-level array');
  }
  return jsonData;
};

export const parseJsonlFileContent = (
  text: string | Record<string, unknown>
): ParsedFileContent => {
  if (typeof text === 'object') {
    return [text as Record<string, unknown>];
  }

  return text
    .trim()
    .split('\n')
    .filter((line) => line.trim() !== '')
    .map((line) => JSON.parse(line));
};

export const convertToJsonFormat = (data: ParsedFileContent): string => {
  return JSON.stringify(data, null, 2);
};

export const convertToJsonlFormat = (data: ParsedFileContent): string => {
  return data.map((item) => JSON.stringify(item)).join('\n');
};

export const removeStringFromText = (text: string, stringToRemove: string): string => {
  return text.split(stringToRemove).join('');
};

export type RemoveMessagesResult = {
  modifiedText: string | undefined;
  firstRemovedContent: string | undefined;
};

/**
 * Removes messages by role from a text string.
 * @param text - The text string to process.
 * @param role - The role of the messages to remove.
 * @param fileExtension - The file extension of the file.
 * @returns A tuple containing [modifiedText, firstRemovedContent]
 */
export const removeMessagesByRole = (
  text: string,
  role: string = 'system',
  fileExtension: SupportedFileExtension
): [string | undefined, string | undefined] => {
  // Parse the preview text into rows
  const rows = parseFileContent(text, fileExtension);
  if (!rows || rows.length === 0) {
    throw new Error('No rows found in text');
  }

  let firstRemovedContent: string | undefined;
  // Process each row to remove messages of specified role and extract the first removed content
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    if (!row.messages || !Array.isArray(row.messages)) continue;

    // Find and remove messages of specified role
    const messageIndex = row.messages.findIndex(
      (msg: { role: string; content: string }) => msg.role === role
    );

    if (messageIndex !== -1) {
      // For the first row, extract the content of the removed message
      if (i === 0) {
        const messageContent = row.messages[messageIndex].content;
        // Escape the content to match how it appears in the raw JSON
        firstRemovedContent = JSON.stringify(messageContent).slice(1, -1);
      }
      // Remove the message
      row.messages.splice(messageIndex, 1);
    }
  }
  // Convert the modified data back to the appropriate format
  const modifiedText = rowsToString(rows, fileExtension);
  return [modifiedText, firstRemovedContent];
};

/**
 * Converts an array of parsed file content rows to a string.
 * @param rows - The array of parsed file content rows.
 * @param fileExtension - The file extension of the file.
 * @param maxRows - The maximum number of rows to process.
 * @returns A string representation of the parsed file content.
 */
export const rowsToString = (
  rows: ParsedFileContent,
  fileExtension: SupportedFileExtension,
  maxRows?: number
): string => {
  const rowsToProcess = maxRows ? rows.slice(0, maxRows) : rows;
  const processedRows = rowsToProcess.map((row: Record<string, unknown>) => JSON.stringify(row));

  if (fileExtension === '.json') {
    return `[${processedRows.join(',')}]`;
  } else {
    return processedRows.join('\n');
  }
};
