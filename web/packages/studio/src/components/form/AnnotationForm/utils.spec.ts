// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { buildAssistantResponse } from '@nemo/common/src/models/utils';
import { formToReviewerAnnotationEvent } from '@studio/components/form/AnnotationForm/utils';

describe('formToReviewerAnnotationEvent', () => {
  it('should return a ReviewerAnnotationEvent', () => {
    const event = formToReviewerAnnotationEvent({
      modelResponse: 'test',
      thumb: 'positive',
      rating: 0.5,
    });
    expect(event).toEqual({
      event_type: 'reviewer_annotation',
      thumb: 'up',
      rating: 0.5,
    });
  });
  it('should handle response override', () => {
    const responseOverride = buildAssistantResponse('test2');
    const event = formToReviewerAnnotationEvent({
      modelResponse: 'test',
      responseOverride,
    });
    expect(event).toEqual({
      event_type: 'reviewer_annotation',
      response_override: responseOverride,
    });
  });

  it('should not return a response override if the model response is the same as the response override', () => {
    const event = formToReviewerAnnotationEvent({
      modelResponse: 'test',
      responseOverride: buildAssistantResponse('test'),
    });
    expect(event).toEqual({
      event_type: 'reviewer_annotation',
    });
    expect(event.response_override).toBeUndefined();
  });
});
