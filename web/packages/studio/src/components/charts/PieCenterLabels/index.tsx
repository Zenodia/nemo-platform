// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useDrawingArea } from '@mui/x-charts';
import { FC } from 'react';

interface Props {
  labels?: string[];
}
/**
 * Allows placement of some text within the center of a MUI PieChart. There are some unique considerations since
 * the text is meant to be rendered within an <svg> tag.
 * labels - A list of length 1 or 2 that renders position calculated <text> tags.
 */
export const PieCenterLabels: FC<Props> = ({ labels }) => {
  const { width, height, left, top } = useDrawingArea();
  const trueCenter = top + height / 2;
  if (!labels || (labels.length !== 1 && labels.length !== 2)) {
    return <div>Unsupported labels length</div>;
  }
  if (labels?.length === 1) {
    const label = labels[0];
    return (
      <text
        key={label}
        x={left + width / 2}
        y={trueCenter}
        className="text-[14px] fill-[var(--text-color-base)] whitespace-pre-line text-center dominant-baseline-central [&_+_text]:text-[32px]"
        textAnchor="middle"
        dominantBaseline="central"
      >
        {label}
      </text>
    );
  }
  return labels?.map((label, index) => {
    const isBigText = index === 0;
    const rowHeight = isBigText ? 32 : 14;
    const startY = isBigText ? trueCenter - rowHeight / 2 : trueCenter + rowHeight;
    return (
      <text
        key={label}
        x={left + width / 2}
        y={startY}
        className={`fill-[var(--text-color-base)] whitespace-pre-line text-center dominant-baseline-central ${isBigText ? '[&_+_text]:text-[32px] text-[14px]' : 'text-[14px]'}`}
        textAnchor="middle"
        dominantBaseline="central"
      >
        {label}
      </text>
    );
  });
};
