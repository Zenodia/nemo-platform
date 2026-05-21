// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { UserActionEvent as UserActionEventType } from '@nemo/sdk/generated/platform/schema';
import { UserActionEvent } from '@studio/components/IntakeEventsList/components/UserActionEvent';
import { TestProviders } from '@studio/tests/util/TestProviders';
import { render, screen } from '@testing-library/react';

describe('UserActionEvent', () => {
  const baseEvent: UserActionEventType = {
    id: 'event-1',
    event_type: 'user_action',
    created_at: '2024-01-15T10:30:00Z',
    created_by: { name: 'Bob Smith' },
    action: 'code_copied',
  };

  it('renders the made an action text', () => {
    render(
      <TestProviders>
        <UserActionEvent event={baseEvent} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('made an action')).toBeInTheDocument();
  });

  it('renders the actor name from created_by string', () => {
    render(
      <TestProviders>
        <UserActionEvent event={baseEvent} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Bob Smith')).toBeInTheDocument();
  });

  it('renders actor name from created_by object with name', () => {
    const event: UserActionEventType = {
      ...baseEvent,
      created_by: { name: 'Robert Smith' },
    };

    render(
      <TestProviders>
        <UserActionEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Robert Smith')).toBeInTheDocument();
  });

  it('renders the action label and value', () => {
    render(
      <TestProviders>
        <UserActionEvent event={baseEvent} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Action')).toBeInTheDocument();
    expect(screen.getByText('code_copied')).toBeInTheDocument();
  });

  it('renders different action names', () => {
    const event: UserActionEventType = {
      ...baseEvent,
      action: 'share_clicked',
    };

    render(
      <TestProviders>
        <UserActionEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('share_clicked')).toBeInTheDocument();
  });

  it('renders metadata when provided', () => {
    const event: UserActionEventType = {
      ...baseEvent,
      metadata: {
        user_id: '12345',
        item_id: 'product_456',
      },
    };

    render(
      <TestProviders>
        <UserActionEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Metadata')).toBeInTheDocument();
    expect(screen.getByText(/"user_id": "12345"/)).toBeInTheDocument();
    expect(screen.getByText(/"item_id": "product_456"/)).toBeInTheDocument();
  });

  it('does not render metadata section when metadata is empty', () => {
    const event: UserActionEventType = {
      ...baseEvent,
      metadata: {},
    };

    render(
      <TestProviders>
        <UserActionEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.queryByText('Metadata')).not.toBeInTheDocument();
  });

  it('does not render metadata section when metadata is undefined', () => {
    const event: UserActionEventType = {
      ...baseEvent,
      metadata: undefined,
    };

    render(
      <TestProviders>
        <UserActionEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.queryByText('Metadata')).not.toBeInTheDocument();
  });

  it('renders metadata with various value types', () => {
    const event: UserActionEventType = {
      ...baseEvent,
      metadata: {
        count: '42',
        variant: 'variant_b',
        enabled: 'true',
      },
    };

    render(
      <TestProviders>
        <UserActionEvent event={event} isLast={false} />
      </TestProviders>
    );

    expect(screen.getByText('Metadata')).toBeInTheDocument();
    expect(screen.getByText(/"count": "42"/)).toBeInTheDocument();
    expect(screen.getByText(/"variant": "variant_b"/)).toBeInTheDocument();
    expect(screen.getByText(/"enabled": "true"/)).toBeInTheDocument();
  });
});
