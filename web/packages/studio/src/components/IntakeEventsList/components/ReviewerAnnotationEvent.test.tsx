// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ReviewerAnnotationEvent as ReviewerAnnotationEventType } from '@nemo/sdk/generated/platform/schema';
import { ReviewerAnnotationEvent } from '@studio/components/IntakeEventsList/components/ReviewerAnnotationEvent';
import { TestProviders } from '@studio/tests/util/TestProviders';
import { render, screen } from '@testing-library/react';

describe('ReviewerAnnotationEvent', () => {
  const baseEvent: ReviewerAnnotationEventType = {
    id: 'event-1',
    event_type: 'reviewer_annotation',
    created_at: '2024-01-15T10:30:00Z',
    created_by: { name: 'John Doe' },
  };

  it('renders the annotated action text', () => {
    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={baseEvent} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('annotated')).toBeInTheDocument();
  });

  it('renders the actor name from created_by string', () => {
    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={baseEvent} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('renders actor name from created_by object with name property', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      created_by: { name: 'Jane Smith' },
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('renders thumbs up tag when thumb is "up"', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      thumb: 'up',
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    // The tag should have green color indicator
    const tag = screen.getByTestId('nv-tag-root');
    expect(tag).toHaveClass('nv-tag--color-green');
  });

  it('renders thumbs down tag when thumb is "down"', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      thumb: 'down',
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    // The tag should have red color indicator
    const tag = screen.getByTestId('nv-tag-root');
    expect(tag).toHaveClass('nv-tag--color-red');
  });

  it('does not render thumb tag when thumb is not provided', () => {
    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={baseEvent} isLast={false} />
      </TestProviders>
    );

    expect(screen.queryByTestId('nv-tag-root')).not.toBeInTheDocument();
  });

  it('renders rating when provided', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      rating: 4,
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Rating')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
  });

  it('renders rating value of 0', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      rating: 0,
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Rating')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('renders rewrite when provided', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      rewrite: 'This is a better response.',
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Rewrite')).toBeInTheDocument();
    expect(screen.getByText('This is a better response.')).toBeInTheDocument();
  });

  it('renders opinion when provided', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      opinion: 'The response needs improvement.',
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Opinion')).toBeInTheDocument();
    expect(screen.getByText('The response needs improvement.')).toBeInTheDocument();
  });

  it('renders categories when provided', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      categories: { helpfulness: 5, accuracy: 4 },
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Categories')).toBeInTheDocument();
    // Categories are rendered as JSON
    expect(screen.getByText(/"helpfulness": 5/)).toBeInTheDocument();
    expect(screen.getByText(/"accuracy": 4/)).toBeInTheDocument();
  });

  it('does not render categories when empty object', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      categories: {},
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.queryByText('Categories')).not.toBeInTheDocument();
  });

  it('renders response_override when provided', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      response_override: {
        choices: [{ message: { role: 'assistant', content: 'Corrected response' } }],
      },
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Override')).toBeInTheDocument();
  });

  it('does not render response_override when empty object', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      response_override: {},
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.queryByText('Override')).not.toBeInTheDocument();
  });

  it('renders multiple content sections', () => {
    const event: ReviewerAnnotationEventType = {
      ...baseEvent,
      rating: 3,
      opinion: 'Needs work',
      rewrite: 'Better version',
    };

    render(
      <TestProviders>
        <ReviewerAnnotationEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Rating')).toBeInTheDocument();
    expect(screen.getByText('Opinion')).toBeInTheDocument();
    expect(screen.getByText('Rewrite')).toBeInTheDocument();
  });
});
