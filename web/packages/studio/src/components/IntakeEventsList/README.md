# IntakeEventsList Component

Displays a timeline-based activity feed of events (annotations, actions, feedback) for an intake entry.

## Overview

This component renders all events associated with an intake entry using a **timeline layout** with:

- **Timeline icons** with connecting vertical lines
- **Actor and action text** in "{Actor} {action verb}" format
- **Relative timestamps**
- **Overflow menu** for actions (e.g., Delete)
- **Remaining data** displaying event data based on event type

## Event Types

| Event Type            | Icon         | Action Text          |
| --------------------- | ------------ | -------------------- |
| `reviewer_annotation` | Pencil       | "annotated."         |
| `user_action`         | AccountCheck | "made an action."    |
| `user_feedback`       | ChatNew      | "provided feedback." |
