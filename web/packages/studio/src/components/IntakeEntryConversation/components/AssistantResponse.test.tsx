// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { FlexibleMessage, ReviewerAnnotationEvent } from '@nemo/sdk/generated/platform/schema';
import { AssistantResponse } from '@studio/components/IntakeEntryConversation/components/AssistantResponse';
import { render, screen } from '@testing-library/react';

const createAssistantMessage = (content: string): FlexibleMessage => ({
  role: 'assistant',
  content,
});

describe('AssistantResponse', () => {
  describe('basic rendering (no annotation)', () => {
    it('renders the Assistant label', () => {
      const message = createAssistantMessage('Hello, how can I help?');

      render(<AssistantResponse message={message} />);

      expect(screen.getByText('Assistant')).toBeInTheDocument();
    });

    it('renders the message content', () => {
      const message = createAssistantMessage('Hello, how can I help?');

      render(<AssistantResponse message={message} />);

      expect(screen.getByText('Hello, how can I help?')).toBeInTheDocument();
    });

    it('does not apply disabled background styling', () => {
      const message = createAssistantMessage('Hello, how can I help?');

      render(<AssistantResponse message={message} />);

      expect(screen.getByTestId('message-content-block')).not.toHaveClass(
        'bg-interaction-disabled'
      );
    });

    it('does not render ThumbStatus when no annotation', () => {
      const message = createAssistantMessage('Hello, how can I help?');

      render(<AssistantResponse message={message} />);

      expect(screen.queryByTestId('thumb-up-icon')).not.toBeInTheDocument();
      expect(screen.queryByTestId('thumb-down-icon')).not.toBeInTheDocument();
    });
  });

  describe('rendering with annotation', () => {
    const annotationWithThumbUp: ReviewerAnnotationEvent = {
      thumb: 'up',
    };

    const annotationWithRewrite: ReviewerAnnotationEvent = {
      thumb: 'down',
      response_override: {
        choices: [{ message: { content: 'Rewritten response' } }],
      },
    };

    it('applies disabled background styling when annotation is present', () => {
      const message = createAssistantMessage('Original response');

      render(<AssistantResponse message={message} annotation={annotationWithThumbUp} />);

      expect(screen.getByTestId('message-content-block')).toHaveClass('bg-interaction-disabled');
    });

    it('renders ThumbStatus when annotation is present', () => {
      const message = createAssistantMessage('Original response');

      render(<AssistantResponse message={message} annotation={annotationWithThumbUp} />);

      expect(screen.getByTestId('thumb-up-icon')).toBeInTheDocument();
      expect(screen.getByTestId('thumb-down-icon')).toBeInTheDocument();
    });

    it('renders Annotation with rewrite content when present', () => {
      const message = createAssistantMessage('Original response');

      render(<AssistantResponse message={message} annotation={annotationWithRewrite} />);

      expect(screen.getByTestId('rewrite-content')).toBeInTheDocument();
      expect(screen.getByText('Rewritten response')).toBeInTheDocument();
    });

    it('highlights thumb based on annotation rating', () => {
      const message = createAssistantMessage('Original response');

      render(<AssistantResponse message={message} annotation={annotationWithThumbUp} />);

      expect(screen.getByTestId('thumb-up-icon')).toHaveClass('text-accent-green');
      expect(screen.getByTestId('thumb-down-icon')).not.toHaveClass('text-accent-red');
    });
  });

  describe('message content extraction', () => {
    it('extracts and displays string content from FlexibleMessage', () => {
      const message = createAssistantMessage('This is a test message');

      render(<AssistantResponse message={message} />);

      expect(screen.getByText('This is a test message')).toBeInTheDocument();
    });

    it('handles array content format (OpenAI multi-part messages)', () => {
      const message: FlexibleMessage = {
        role: 'assistant',
        content: [{ type: 'text', text: 'Multi-part content' }],
      };

      render(<AssistantResponse message={message} />);

      expect(screen.getByText('Multi-part content')).toBeInTheDocument();
    });

    it('renders empty content gracefully', () => {
      const message = createAssistantMessage('');

      render(<AssistantResponse message={message} />);

      expect(screen.getByText('Assistant')).toBeInTheDocument();
      expect(screen.getByTestId('chat-message')).toBeInTheDocument();
    });
  });
});
