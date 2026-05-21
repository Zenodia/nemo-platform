// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ThumbTag } from '@studio/components/IntakeEventsList/components/ThumbTag';
import { render, screen } from '@testing-library/react';

describe('ThumbTag', () => {
  it('renders "Positive" text when thumb is up', () => {
    render(<ThumbTag thumb="up" />);

    expect(screen.getByText('Positive')).toBeInTheDocument();
  });

  it('renders "Negative" text when thumb is down', () => {
    render(<ThumbTag thumb="down" />);

    expect(screen.getByText('Negative')).toBeInTheDocument();
  });

  it('renders green tag when thumb is up', () => {
    render(<ThumbTag thumb="up" />);

    const tag = screen.getByTestId('nv-tag-root');
    expect(tag).toHaveClass('nv-tag--color-green');
  });

  it('renders red tag when thumb is down', () => {
    render(<ThumbTag thumb="down" />);

    const tag = screen.getByTestId('nv-tag-root');
    expect(tag).toHaveClass('nv-tag--color-red');
  });
});
