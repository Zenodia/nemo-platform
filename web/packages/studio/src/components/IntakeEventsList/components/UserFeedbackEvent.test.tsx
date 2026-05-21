// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { UserFeedbackEvent as UserFeedbackEventType } from '@nemo/sdk/generated/platform/schema';
import { UserFeedbackEvent } from '@studio/components/IntakeEventsList/components/UserFeedbackEvent';
import { TestProviders } from '@studio/tests/util/TestProviders';
import { render, screen } from '@testing-library/react';

describe('UserFeedbackEvent', () => {
  const baseEvent: UserFeedbackEventType = {
    id: 'event-1',
    event_type: 'user_feedback',
    created_at: '2024-01-15T10:30:00Z',
    created_by: { name: 'Alice Johnson' },
  };

  it('renders the provided feedback action text', () => {
    render(
      <TestProviders>
        <UserFeedbackEvent event={baseEvent} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('provided feedback')).toBeInTheDocument();
  });

  it('renders the actor name from created_by string', () => {
    render(
      <TestProviders>
        <UserFeedbackEvent event={baseEvent} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
  });

  it('renders actor name from created_by object with username', () => {
    const event: UserFeedbackEventType = {
      ...baseEvent,
      created_by: { username: 'alice_j' },
    };

    render(
      <TestProviders>
        <UserFeedbackEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('alice_j')).toBeInTheDocument();
  });

  it('renders thumbs up tag when thumb is "up"', () => {
    const event: UserFeedbackEventType = {
      ...baseEvent,
      thumb: 'up',
    };

    render(
      <TestProviders>
        <UserFeedbackEvent event={event} isLast={false} />
      </TestProviders>
    );

    const tag = screen.getByTestId('nv-tag-root');
    expect(tag).toHaveClass('nv-tag--color-green');
  });

  it('renders thumbs down tag when thumb is "down"', () => {
    const event: UserFeedbackEventType = {
      ...baseEvent,
      thumb: 'down',
    };

    render(
      <TestProviders>
        <UserFeedbackEvent event={event} isLast={false} />
      </TestProviders>
    );

    const tag = screen.getByTestId('nv-tag-root');
    expect(tag).toHaveClass('nv-tag--color-red');
  });

  it('does not render thumb tag when thumb is not provided', () => {
    render(
      <TestProviders>
        <UserFeedbackEvent event={baseEvent} isLast={false} />
      </TestProviders>
    );

    expect(screen.queryByTestId('nv-tag-root')).not.toBeInTheDocument();
  });

  it('renders rating when provided', () => {
    const event: UserFeedbackEventType = {
      ...baseEvent,
      rating: 5,
    };

    render(
      <TestProviders>
        <UserFeedbackEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Rating')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('renders rating value of 0', () => {
    const event: UserFeedbackEventType = {
      ...baseEvent,
      rating: 0,
    };

    render(
      <TestProviders>
        <UserFeedbackEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Rating')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('renders rewrite when provided', () => {
    const event: UserFeedbackEventType = {
      ...baseEvent,
      rewrite: 'Here is what I expected the response to be.',
    };

    render(
      <TestProviders>
        <UserFeedbackEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Rewrite')).toBeInTheDocument();
    expect(screen.getByText('Here is what I expected the response to be.')).toBeInTheDocument();
  });

  it('renders opinion when provided', () => {
    const event: UserFeedbackEventType = {
      ...baseEvent,
      opinion: 'This response was very helpful!',
    };

    render(
      <TestProviders>
        <UserFeedbackEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Opinion')).toBeInTheDocument();
    expect(screen.getByText('This response was very helpful!')).toBeInTheDocument();
  });

  it('renders categories when provided', () => {
    const event: UserFeedbackEventType = {
      ...baseEvent,
      categories: { tone: 'professional', clarity: 5 },
    };

    render(
      <TestProviders>
        <UserFeedbackEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Categories')).toBeInTheDocument();
    expect(screen.getByText(/"tone": "professional"/)).toBeInTheDocument();
    expect(screen.getByText(/"clarity": 5/)).toBeInTheDocument();
  });

  it('does not render categories when empty object', () => {
    const event: UserFeedbackEventType = {
      ...baseEvent,
      categories: {},
    };

    render(
      <TestProviders>
        <UserFeedbackEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.queryByText('Categories')).not.toBeInTheDocument();
  });

  it('renders multiple content sections', () => {
    const event: UserFeedbackEventType = {
      ...baseEvent,
      thumb: 'up',
      rating: 4,
      opinion: 'Great response',
      rewrite: 'Could add more detail here',
    };

    render(
      <TestProviders>
        <UserFeedbackEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Rating')).toBeInTheDocument();
    expect(screen.getByText('Opinion')).toBeInTheDocument();
    expect(screen.getByText('Rewrite')).toBeInTheDocument();
  });
});
