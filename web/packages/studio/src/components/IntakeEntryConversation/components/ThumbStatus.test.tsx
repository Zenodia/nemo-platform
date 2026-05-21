// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ReviewerAnnotationEvent } from '@nemo/sdk/generated/platform/schema';
import { ThumbStatus } from '@studio/components/IntakeEntryConversation/components/ThumbStatus';
import { render, screen } from '@testing-library/react';

describe('ThumbStatus', () => {
  it('renders both thumb icons', () => {
    const annotation: ReviewerAnnotationEvent = {};

    render(<ThumbStatus annotation={annotation} />);

    expect(screen.getByTestId('thumb-up-icon')).toBeInTheDocument();
    expect(screen.getByTestId('thumb-down-icon')).toBeInTheDocument();
  });

  it('highlights ThumbUp green when thumb is up', () => {
    const annotation: ReviewerAnnotationEvent = { thumb: 'up' };

    render(<ThumbStatus annotation={annotation} />);

    expect(screen.getByTestId('thumb-up-icon')).toHaveClass('text-accent-green');
    expect(screen.getByTestId('thumb-down-icon')).not.toHaveClass('text-accent-red');
  });

  it('highlights ThumbDown red when thumb is down', () => {
    const annotation: ReviewerAnnotationEvent = { thumb: 'down' };

    render(<ThumbStatus annotation={annotation} />);

    expect(screen.getByTestId('thumb-up-icon')).not.toHaveClass('text-accent-green');
    expect(screen.getByTestId('thumb-down-icon')).toHaveClass('text-accent-red');
  });

  it('does not highlight either icon when thumb is undefined', () => {
    const annotation: ReviewerAnnotationEvent = {};

    render(<ThumbStatus annotation={annotation} />);

    expect(screen.getByTestId('thumb-up-icon')).not.toHaveClass('text-accent-green');
    expect(screen.getByTestId('thumb-down-icon')).not.toHaveClass('text-accent-red');
  });

  describe('accessibility', () => {
    it('has appropriate aria-label for thumbs up rating', () => {
      const annotation: ReviewerAnnotationEvent = { thumb: 'up' };

      render(<ThumbStatus annotation={annotation} />);

      expect(screen.getByLabelText('Reviewer rating: thumbs up')).toBeInTheDocument();
    });

    it('has appropriate aria-label for thumbs down rating', () => {
      const annotation: ReviewerAnnotationEvent = { thumb: 'down' };

      render(<ThumbStatus annotation={annotation} />);

      expect(screen.getByLabelText('Reviewer rating: thumbs down')).toBeInTheDocument();
    });

    it('has appropriate aria-label when no rating provided', () => {
      const annotation: ReviewerAnnotationEvent = {};

      render(<ThumbStatus annotation={annotation} />);

      expect(screen.getByLabelText('Reviewer rating: no rating provided')).toBeInTheDocument();
    });

    it('uses status role for screen reader announcements', () => {
      const annotation: ReviewerAnnotationEvent = { thumb: 'up' };

      render(<ThumbStatus annotation={annotation} />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('hides inactive icon from screen readers when thumbs up', () => {
      const annotation: ReviewerAnnotationEvent = { thumb: 'up' };

      render(<ThumbStatus annotation={annotation} />);

      expect(screen.getByTestId('thumb-up-icon')).toHaveAttribute('aria-hidden', 'false');
      expect(screen.getByTestId('thumb-down-icon')).toHaveAttribute('aria-hidden', 'true');
    });

    it('hides inactive icon from screen readers when thumbs down', () => {
      const annotation: ReviewerAnnotationEvent = { thumb: 'down' };

      render(<ThumbStatus annotation={annotation} />);

      expect(screen.getByTestId('thumb-up-icon')).toHaveAttribute('aria-hidden', 'true');
      expect(screen.getByTestId('thumb-down-icon')).toHaveAttribute('aria-hidden', 'false');
    });

    it('hides both icons from screen readers when no rating', () => {
      const annotation: ReviewerAnnotationEvent = {};

      render(<ThumbStatus annotation={annotation} />);

      expect(screen.getByTestId('thumb-up-icon')).toHaveAttribute('aria-hidden', 'true');
      expect(screen.getByTestId('thumb-down-icon')).toHaveAttribute('aria-hidden', 'true');
    });
  });
});
