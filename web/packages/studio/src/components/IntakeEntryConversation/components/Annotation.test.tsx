// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ReviewerAnnotationEvent } from '@nemo/sdk/generated/platform/schema';
import { Annotation } from '@studio/components/IntakeEntryConversation/components/Annotation';
import { render, screen } from '@testing-library/react';

const createAnnotationWithResponseOverride = (content?: string): ReviewerAnnotationEvent => ({
  thumb: 'down',
  response_override: content !== undefined ? { choices: [{ message: { content } }] } : undefined,
});

const createAnnotationWithRewrite = (rewrite?: string): ReviewerAnnotationEvent => ({
  thumb: 'down',
  rewrite,
});

describe('Annotation', () => {
  describe('null conditions', () => {
    it('returns null when annotation has no rewrite or response_override', () => {
      const annotation: ReviewerAnnotationEvent = { thumb: 'up' };

      render(<Annotation annotation={annotation} />);

      expect(screen.queryByText('Rewrite')).not.toBeInTheDocument();
      expect(screen.queryByTestId('rewrite-content')).not.toBeInTheDocument();
    });

    it('returns null when response_override has no choices', () => {
      const annotation: ReviewerAnnotationEvent = {
        thumb: 'down',
        response_override: {},
      };

      render(<Annotation annotation={annotation} />);

      expect(screen.queryByText('Rewrite')).not.toBeInTheDocument();
      expect(screen.queryByTestId('rewrite-content')).not.toBeInTheDocument();
    });

    it('returns null when choices is empty array', () => {
      const annotation: ReviewerAnnotationEvent = {
        thumb: 'down',
        response_override: { choices: [] },
      };

      render(<Annotation annotation={annotation} />);

      expect(screen.queryByText('Rewrite')).not.toBeInTheDocument();
      expect(screen.queryByTestId('rewrite-content')).not.toBeInTheDocument();
    });

    it('returns null when response_override content is empty string', () => {
      const annotation = createAnnotationWithResponseOverride('');

      render(<Annotation annotation={annotation} />);

      expect(screen.queryByText('Rewrite')).not.toBeInTheDocument();
      expect(screen.queryByTestId('rewrite-content')).not.toBeInTheDocument();
    });

    it('returns null when response_override content is whitespace only', () => {
      const annotation = createAnnotationWithResponseOverride('   ');

      render(<Annotation annotation={annotation} />);

      expect(screen.queryByText('Rewrite')).not.toBeInTheDocument();
      expect(screen.queryByTestId('rewrite-content')).not.toBeInTheDocument();
    });

    it('returns null when rewrite is empty string', () => {
      const annotation = createAnnotationWithRewrite('');

      render(<Annotation annotation={annotation} />);

      expect(screen.queryByText('Rewrite')).not.toBeInTheDocument();
      expect(screen.queryByTestId('rewrite-content')).not.toBeInTheDocument();
    });

    it('returns null when rewrite is whitespace only', () => {
      const annotation = createAnnotationWithRewrite('   ');

      render(<Annotation annotation={annotation} />);

      expect(screen.queryByText('Rewrite')).not.toBeInTheDocument();
      expect(screen.queryByTestId('rewrite-content')).not.toBeInTheDocument();
    });
  });

  describe('rendering with response_override', () => {
    it('renders Rewrite label', () => {
      const annotation = createAnnotationWithResponseOverride('This is a rewritten response.');

      render(<Annotation annotation={annotation} />);

      expect(screen.getByText('Rewrite')).toBeInTheDocument();
    });

    it('renders the rewrite content', () => {
      const annotation = createAnnotationWithResponseOverride('This is a rewritten response.');

      render(<Annotation annotation={annotation} />);

      expect(screen.getByTestId('rewrite-content')).toBeInTheDocument();
      expect(screen.getByText('This is a rewritten response.')).toBeInTheDocument();
    });
  });

  describe('rendering with rewrite field', () => {
    it('renders Rewrite label', () => {
      const annotation = createAnnotationWithRewrite('Direct rewrite content.');

      render(<Annotation annotation={annotation} />);

      expect(screen.getByText('Rewrite')).toBeInTheDocument();
    });

    it('renders the rewrite content', () => {
      const annotation = createAnnotationWithRewrite('Direct rewrite content.');

      render(<Annotation annotation={annotation} />);

      expect(screen.getByTestId('rewrite-content')).toBeInTheDocument();
      expect(screen.getByText('Direct rewrite content.')).toBeInTheDocument();
    });
  });

  describe('rewrite precedence', () => {
    it('uses rewrite field over response_override when both present', () => {
      const annotation: ReviewerAnnotationEvent = {
        thumb: 'down',
        rewrite: 'Content from rewrite field',
        response_override: {
          choices: [{ message: { content: 'Content from response_override' } }],
        },
      };

      render(<Annotation annotation={annotation} />);

      expect(screen.getByText('Content from rewrite field')).toBeInTheDocument();
      expect(screen.queryByText('Content from response_override')).not.toBeInTheDocument();
    });
  });
});
