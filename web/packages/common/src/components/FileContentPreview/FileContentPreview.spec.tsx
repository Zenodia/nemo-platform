// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { FileContentPreview } from '@nemo/common/src/components/FileContentPreview/index';
import { render, screen } from '@testing-library/react';

// Mock papaparse
vi.mock('papaparse', () => ({
  default: {
    parse: vi.fn((content: string) => {
      // Simple CSV parser mock
      const lines = content.trim().split('\n');
      if (lines.length === 0) {
        return { data: [], meta: { fields: [] }, errors: [] };
      }

      const headers = lines[0].split(',');
      const data = lines.slice(1).map((line) => {
        const values = line.split(',');
        const row: Record<string, string> = {};
        headers.forEach((header, index) => {
          row[header] = values[index] || '';
        });
        return row;
      });

      return {
        data,
        meta: { fields: headers },
        errors: [],
      };
    }),
  },
}));

describe('FileContentPreview', () => {
  const defaultFile = { path: 'test.txt', url: '' };

  describe('loading state', () => {
    it('renders spinner when loading', () => {
      render(<FileContentPreview file={defaultFile} isLoading error={null} content={undefined} />);

      expect(screen.getByLabelText('Loading...')).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('renders error message when error is provided', () => {
      const error = new Error('Failed to fetch file');

      render(<FileContentPreview file={defaultFile} isLoading={false} error={error} />);

      expect(screen.getByText('Error: Failed to fetch file')).toBeInTheDocument();
    });

    it('renders generic error message when error has no message', () => {
      const error = new Error();
      error.message = '';

      render(<FileContentPreview file={defaultFile} isLoading={false} error={error} />);

      expect(screen.getByText('Error: Failed to load file')).toBeInTheDocument();
    });
  });

  describe('no content state', () => {
    it('renders "No content available" when content is undefined', () => {
      render(
        <FileContentPreview file={defaultFile} isLoading={false} error={null} content={undefined} />
      );

      expect(screen.getByText('No content available')).toBeInTheDocument();
    });

    it('renders "No content available" when content is empty string', () => {
      render(<FileContentPreview file={defaultFile} isLoading={false} error={null} content="" />);

      expect(screen.getByText('No content available')).toBeInTheDocument();
    });
  });

  describe('JSON files', () => {
    it('renders JSON content with CodeSnippet', () => {
      const jsonFile = { path: 'data.json', url: '' };
      const content = '{"key": "value"}';

      render(
        <FileContentPreview file={jsonFile} isLoading={false} error={null} content={content} />
      );

      // CodeSnippet should render the content
      expect(screen.getByText('{"key": "value"}')).toBeInTheDocument();
    });

    it('renders JSONL content with CodeSnippet', () => {
      const jsonlFile = { path: 'data.jsonl', url: '' };
      const content = '{"line": 1}\n{"line": 2}';

      render(
        <FileContentPreview file={jsonlFile} isLoading={false} error={null} content={content} />
      );

      // Verify CodeSnippet renders with the content
      const codeSnippet = screen.getByTestId('nv-code-snippet-root');
      expect(codeSnippet).toBeInTheDocument();
      expect(codeSnippet).toHaveTextContent('{"line": 1}');
      expect(codeSnippet).toHaveTextContent('{"line": 2}');
    });
  });

  describe('CSV files', () => {
    it('renders CSV content in a table', () => {
      const csvFile = { path: 'data.csv', url: '' };
      const content = 'name,age\nAlice,30\nBob,25';

      render(
        <FileContentPreview file={csvFile} isLoading={false} error={null} content={content} />
      );

      // Table headers
      expect(screen.getByText('name')).toBeInTheDocument();
      expect(screen.getByText('age')).toBeInTheDocument();

      // Table data
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
    });
  });

  describe('plain text fallback', () => {
    it('renders plain text content with CodeSnippet', () => {
      const txtFile = { path: 'readme.txt', url: '' };
      const content = 'This is plain text content';

      render(
        <FileContentPreview file={txtFile} isLoading={false} error={null} content={content} />
      );

      expect(screen.getByText('This is plain text content')).toBeInTheDocument();
    });

    it('renders markdown content with CodeSnippet', () => {
      const mdFile = { path: 'readme.md', url: '' };
      const content = '# Heading\n\nSome text';

      render(<FileContentPreview file={mdFile} isLoading={false} error={null} content={content} />);

      // Verify CodeSnippet renders with the content
      const codeSnippet = screen.getByTestId('nv-code-snippet-root');
      expect(codeSnippet).toBeInTheDocument();
      expect(codeSnippet).toHaveTextContent('# Heading');
      expect(codeSnippet).toHaveTextContent('Some text');
    });
  });

  describe('file type detection', () => {
    it('detects JSON file by extension', () => {
      const file = { path: 'config.json', url: '' };
      const content = '{"setting": true}';

      render(<FileContentPreview file={file} isLoading={false} error={null} content={content} />);

      // JSON files render in CodeSnippet
      expect(screen.getByText('{"setting": true}')).toBeInTheDocument();
    });

    it('detects JSONL file by extension', () => {
      const file = { path: 'logs.jsonl', url: '' };
      const content = '{"event": "login"}';

      render(<FileContentPreview file={file} isLoading={false} error={null} content={content} />);

      expect(screen.getByText('{"event": "login"}')).toBeInTheDocument();
    });

    it('handles nested file paths', () => {
      const file = { path: 'folder/subfolder/data.json', url: '' };
      const content = '{"nested": true}';

      render(<FileContentPreview file={file} isLoading={false} error={null} content={content} />);

      expect(screen.getByText('{"nested": true}')).toBeInTheDocument();
    });
  });

  describe('with file content from FileListItem', () => {
    it('renders content from file with dataset info', () => {
      const file = {
        path: 'train.jsonl',
        url: 'fileset://org/dataset/train.jsonl',
        dataset: {
          id: 'org/dataset',
          name: 'dataset',
          workspace: 'org',
          description: '',
          purpose: 'dataset' as const,
          storage: { type: 'local' as const, path: '/data' },
          metadata: {},
          custom_fields: {},
          project: 'default',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      };
      const content = '{"example": 1}';

      render(<FileContentPreview file={file} isLoading={false} error={null} content={content} />);

      expect(screen.getByText('{"example": 1}')).toBeInTheDocument();
    });

    it('renders content from file with local content', () => {
      const file = {
        path: 'uploaded.json',
        url: 'blob:http://localhost/abc123',
        content: '{"local": true}',
      };

      render(
        <FileContentPreview file={file} isLoading={false} error={null} content={file.content} />
      );

      expect(screen.getByText('{"local": true}')).toBeInTheDocument();
    });
  });
});
