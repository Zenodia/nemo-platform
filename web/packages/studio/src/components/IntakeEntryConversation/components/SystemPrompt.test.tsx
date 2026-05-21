// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { FlexibleMessage } from '@nemo/sdk/generated/platform/schema';
import { SystemPrompt } from '@studio/components/IntakeEntryConversation/components/SystemPrompt';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

const createSystemMessage = (content: FlexibleMessage['content']): FlexibleMessage => ({
  role: 'system',
  content,
});

describe('SystemPrompt', () => {
  describe('rendering', () => {
    it('renders accordion with system content', async () => {
      const user = userEvent.setup();
      const messages = [createSystemMessage('You are a helpful assistant.')];

      render(<SystemPrompt systemMessages={messages} />);

      expect(screen.getByText('System Prompt')).toBeInTheDocument();

      // Expand accordion to see content
      await user.click(screen.getByTestId('nv-accordion-trigger'));
      expect(screen.getByText('You are a helpful assistant.')).toBeInTheDocument();
    });

    it('displays file size in accordion trigger', () => {
      // "Hello" = 5 bytes
      const messages = [createSystemMessage('Hello')];

      render(<SystemPrompt systemMessages={messages} />);

      expect(screen.getByText('(5B)')).toBeInTheDocument();
    });

    it('combines multiple system messages with double newlines', async () => {
      const user = userEvent.setup();
      const messages = [
        createSystemMessage('First message'),
        createSystemMessage('Second message'),
      ];

      render(<SystemPrompt systemMessages={messages} />);

      // Expand accordion to see content
      await user.click(screen.getByTestId('nv-accordion-trigger'));

      // Both messages should be visible
      expect(screen.getByText(/First message/)).toBeInTheDocument();
      expect(screen.getByText(/Second message/)).toBeInTheDocument();
    });
  });

  describe('null conditions', () => {
    it('returns null when systemMessages is empty array', () => {
      render(<SystemPrompt systemMessages={[]} />);

      expect(screen.queryByTestId('nv-accordion-root')).not.toBeInTheDocument();
    });

    it('returns null when content is empty string', () => {
      const messages = [createSystemMessage('')];

      render(<SystemPrompt systemMessages={messages} />);

      expect(screen.queryByTestId('nv-accordion-root')).not.toBeInTheDocument();
    });

    it('returns null when content is whitespace only', () => {
      const messages = [createSystemMessage('   ')];

      render(<SystemPrompt systemMessages={messages} />);

      expect(screen.queryByTestId('nv-accordion-root')).not.toBeInTheDocument();
    });

    it('returns null when content is single newline', () => {
      const messages = [createSystemMessage('\n')];

      render(<SystemPrompt systemMessages={messages} />);

      expect(screen.queryByTestId('nv-accordion-root')).not.toBeInTheDocument();
    });
  });
});
