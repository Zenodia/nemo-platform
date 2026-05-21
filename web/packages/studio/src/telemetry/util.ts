// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Attributes, HrTime } from '@opentelemetry/api';

/**
 * Converts an OpenTelemetry HrTime tuple to a JavaScript timestamp in milliseconds.
 * OpenTelemetry provides startTime and endTime as [seconds, nanoseconds] tuples.
 * This function converts this to a single JavaScript timestamp in milliseconds.
 *
 * @param hrTime - The HrTime tuple [seconds, nanoseconds]
 * @returns JavaScript timestamp in milliseconds (number)
 */
export const hrTimeToMilliseconds = (hrTime: HrTime): number => {
  // Convert seconds to milliseconds and nanoseconds to milliseconds, then combine
  return hrTime[0] * 1000 + Math.round(hrTime[1] / 1_000_000);
};

export const enhanceFetchSpanName = (originalName: string, attributes: Attributes): string => {
  // FETCH requests (from @opentelemetry/instrumentation-fetch)
  const method = originalName.replace('HTTP ', '');
  const url = attributes['http.url'] || attributes['url.full'];
  const urlPath =
    // URL will error unless it's passed an actual URL
    typeof url === 'string' && /^https?:\/\//.test(url) ? new URL(url).pathname : '';
  return `FETCH ${method}${urlPath ? ` ${urlPath}` : ''}`;
};

export const enhanceXhrSpanName = (originalName: string, attributes: Attributes): string => {
  // XHR requests (from @opentelemetry/instrumentation-xml-http-request)
  const url = attributes['http.url'] || attributes['url.full'];
  const urlPath =
    // URL will error unless it's passed an actual URL
    typeof url === 'string' && /^https?:\/\//.test(url) ? new URL(url).pathname : '';
  return `XHR ${originalName}${urlPath ? ` ${urlPath}` : ''}`;
};

export const enhanceClickSpanName = (attributes: Attributes): string => {
  const targetElement = attributes['event_target_element'] || attributes['target_element'];
  const targetTagName = attributes['event_target_tag_name'] || attributes['target_tag_name'];
  const targetId = attributes['event_target_id'] || attributes['target_id'];
  const targetClass = attributes['event_target_class'] || attributes['target_class'];
  const targetText = attributes['event_target_text'] || attributes['target_text'];

  let clickDetails = 'Click';

  // Build a descriptive string for the clicked element
  if (targetTagName) {
    clickDetails += ` on ${targetTagName.toString().toLowerCase()}`;

    if (targetId) {
      clickDetails += `#${targetId}`;
    } else if (targetClass) {
      clickDetails += `.${targetClass.toString().split(' ')[0]}`;
    } else if (targetText) {
      const text = targetText.toString().trim();
      if (text.length > 0) {
        clickDetails += ` "${text.length > 30 ? text.substring(0, 30) + '...' : text}"`;
      }
    }
  } else if (targetElement) {
    clickDetails += ` on ${targetElement}`;
  }

  return clickDetails;
};

export const enhanceNavigationSpanName = (): string => {
  // Handle navigation events - keep them clean
  return 'Navigation';
};

export const enhanceSubmitSpanName = (attributes: Attributes): string => {
  const targetElement = attributes['event_target_element'] || attributes['target_element'];
  const targetId = attributes['event_target_id'] || attributes['target_id'];

  let submitDetails = 'Form Submit';
  if (targetId) {
    submitDetails += ` #${targetId}`;
  } else if (targetElement) {
    submitDetails += ` ${targetElement}`;
  }

  return submitDetails;
};
