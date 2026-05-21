// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ThumbDirection, type ReviewerAnnotationEvent } from '@nemo/sdk/generated/platform/schema';
import { annotationFormFields } from '@studio/components/form/AnnotationForm/constants';
import { ChatCompletion } from 'openai/resources/index.mjs';
import { z } from 'zod';

export const formToReviewerAnnotationEvent = (
  data: z.infer<typeof annotationFormFields>
): ReviewerAnnotationEvent => {
  const modelResponse = data.modelResponse;
  // Map form thumb values to API ThumbDirection
  const thumbDirection =
    data.thumb === 'positive'
      ? ThumbDirection.up
      : data.thumb === 'negative'
        ? ThumbDirection.down
        : undefined;

  const reviewerEvent: ReviewerAnnotationEvent = {
    event_type: 'reviewer_annotation',
  };
  if (thumbDirection) {
    reviewerEvent.thumb = thumbDirection;
  }
  if (data.rating) {
    reviewerEvent.rating = data.rating;
  }
  if (data.responseOverride && 'choices' in data.responseOverride) {
    const asChoice = (data.responseOverride.choices as ChatCompletion['choices'])[0];
    const responseAsString = asChoice.message?.content;
    reviewerEvent.response_override =
      responseAsString !== modelResponse ? data.responseOverride : undefined;
  }
  return reviewerEvent;
};
