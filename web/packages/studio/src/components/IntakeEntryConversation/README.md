# IntakeEntryConversation

Displays intake entry conversation data with toggleable Chat and JSON view modes.

## Overview

This component renders an intake entry's conversation history in a Panel with a segmented control to switch between two view modes:

- **Chat View**: Interactive chat bubble interface with system prompts, user messages, and assistant responses
- **JSON View**: Raw entry data displayed as syntax-highlighted JSON

## Usage

```tsx
import { IntakeEntryConversation } from '@studio/components/IntakeEntryConversation';

<IntakeEntryConversation entry={selectedEntry} />;
```

## Component Structure

```text
IntakeEntryConversation/
├── index.tsx              # Main component with view mode toggle
├── index.spec.tsx         # Unit tests
├── README.md              # This file
└── components/
    ├── ChatView.tsx       # Renders entry as chat conversation
    ├── JSONView.tsx       # Renders entry as formatted JSON
    ├── SystemPrompt.tsx   # Collapsible accordion for system messages
    ├── LastUserMessage.tsx    # Right-aligned user message bubble
    ├── AssistantResponse.tsx  # Assistant response with annotations
    ├── Annotation.tsx     # Rewrite content display
    └── ThumbStatus.tsx    # Thumb up/down rating indicator
```

## Subcomponents

### ChatView

Parses and displays the entry as a conversational interface:

- **SystemPrompt**: Collapsible accordion showing system messages with a size indicator (e.g., "225.89kB")
- **LastUserMessage**: Right-aligned chat bubble for the user's input
- **AssistantResponse**: Left-aligned chat bubble with optional annotation overlay

### JSONView

Displays the complete entry object as pretty-printed JSON in a collapsible code snippet with syntax highlighting.

## Props

| Prop    | Type    | Required | Description                                   |
| ------- | ------- | -------- | --------------------------------------------- |
| `entry` | `Entry` | Yes      | The intake entry containing conversation data |

## Data Flow

```text
Entry
├── System messages → SystemPrompt (collapsible accordion)
├── Last user message → LastUserMessage (right-aligned bubble)
├── Last assistant message → AssistantResponse (left-aligned bubble)
│   ├── response_override → Annotation (rewrite content)
│   └── thumb rating → ThumbStatus (up/down indicator)
└── Raw data → JSONView (code snippet)
```
