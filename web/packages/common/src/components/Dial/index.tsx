// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Stack, Text } from '@nvidia/foundations-react-core';
import { useEffect, useState } from 'react';

type DialSize = 'l' | 'm' | 's';

interface DialProps {
  /** Value as a percentage (0-100) */
  value: number;
  /** The value to display in the center of the dial */
  displayValue: string | number;
  /** Color of the filled portion of the dial */
  color: string;
  /** Background color of the unfilled portion of the dial */
  backgroundColor?: string;
  /** Size of the dial: 'l' , 'm' , or 's' */
  size?: DialSize;
  /** Duration of the animation in milliseconds */
  animationDuration?: number;
  /** If true, scales the dial to fit its parent container while maintaining aspect ratio */
  scaleToFit?: boolean;
}

export const Dial = ({
  value,
  displayValue,
  color,
  backgroundColor = 'var(--background-color-accent-gray)',
  size = 'm',
  animationDuration = 500,
  scaleToFit = false,
}: DialProps) => {
  // Ensure value is between 0 and 100
  const normalizedValue = Math.min(Math.max(value, 0), 100);

  // Animated value state
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    // Skip animation for 's' size
    if (size === 's') {
      setAnimatedValue(normalizedValue);
      return;
    }

    let startTime: number | null = null;
    let animationFrameId: number;
    const startValue = animatedValue;
    const valueChange = normalizedValue - startValue;

    // If no change, don't animate
    if (valueChange === 0) {
      return;
    }

    const animate = (timestamp: number) => {
      if (startTime === null) {
        startTime = timestamp;
      }

      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / animationDuration, 1);

      // Easing function (ease-out)
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const currentValue = startValue + easeOut * valueChange;

      setAnimatedValue(currentValue);

      if (progress < 1) {
        animationFrameId = requestAnimationFrame(animate);
      }
    };

    animationFrameId = requestAnimationFrame(animate);

    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [normalizedValue, animationDuration, size]);

  // Determine if displayValue is empty and what to display
  const isDisplayValueEmpty = !displayValue && displayValue !== 0;
  const actualDisplayValue = isDisplayValueEmpty ? '—' : displayValue;

  // Size configurations
  const sizeConfig = {
    l: { dimension: 222, strokeWidth: 24 },
    m: { dimension: 100, strokeWidth: 12 },
    s: { dimension: 22, strokeWidth: 4 },
  };

  const config = sizeConfig[size];
  const dimension = config.dimension;
  const strokeWidth = config.strokeWidth;
  const center = dimension / 2;
  const radius = (dimension - strokeWidth) / 2;

  // Calculate the dial arc
  const dialArcDegrees = 360 * 0.75;
  const startAngle = 90 + (360 - dialArcDegrees) / 2; // Start angle to center the arc
  const endAngle = startAngle + dialArcDegrees;

  // Convert angles to radians
  const startRad = (startAngle * Math.PI) / 180;
  const endRad = (endAngle * Math.PI) / 180;

  // Calculate arc path for background
  const bgStartX = center + radius * Math.cos(startRad);
  const bgStartY = center + radius * Math.sin(startRad);
  const bgEndX = center + radius * Math.cos(endRad);
  const bgEndY = center + radius * Math.sin(endRad);

  const backgroundPath = `
    M ${bgStartX} ${bgStartY}
    A ${radius} ${radius} 0 1 1 ${bgEndX} ${bgEndY}
  `;

  // Calculate arc path for filled portion based on value
  const valueAngle = startAngle + (dialArcDegrees * animatedValue) / 100;
  const valueRad = (valueAngle * Math.PI) / 180;
  const valueEndX = center + radius * Math.cos(valueRad);
  const valueEndY = center + radius * Math.sin(valueRad);

  // Determine if we need the large-arc-flag (for arcs > 180 degrees)
  const largeArcFlag = (dialArcDegrees * animatedValue) / 100 > 180 ? 1 : 0;

  const valuePath = `
    M ${bgStartX} ${bgStartY}
    A ${radius} ${radius} 0 ${largeArcFlag} 1 ${valueEndX} ${valueEndY}
  `;

  return (
    <Stack
      className={size === 's' ? 'relative inline-flex' : 'relative inline-block'}
      direction={size === 's' ? 'row' : 'col'}
      align={size === 's' ? 'center' : undefined}
      gap={size === 's' ? '2' : undefined}
    >
      <div
        className="relative"
        /* eslint-disable-next-line no-restricted-syntax */
        style={
          scaleToFit
            ? {
                width: '100%',
                height: '100%',
                maxWidth: dimension,
                maxHeight: dimension,
                aspectRatio: 1,
              }
            : {
                width: dimension,
                height: dimension,
              }
        }
      >
        <svg
          width={scaleToFit ? '100%' : dimension}
          height={scaleToFit ? '100%' : dimension}
          viewBox={`0 0 ${dimension} ${dimension}`}
          /* eslint-disable-next-line no-restricted-syntax */
          style={scaleToFit ? { display: 'block' } : undefined}
        >
          {/* Background arc */}
          <path
            d={backgroundPath}
            fill="none"
            stroke={backgroundColor}
            strokeWidth={strokeWidth}
            strokeLinecap="butt"
          />
          {/* Filled arc based on value */}
          {animatedValue > 0 && (
            <path
              d={valuePath}
              fill="none"
              stroke={color}
              strokeWidth={strokeWidth}
              strokeLinecap="butt"
            />
          )}
          {/* Display value in center (for l and m sizes) - use SVG text when scaling */}
          {size !== 's' && (
            <text
              x={center}
              y={center}
              textAnchor="middle"
              dominantBaseline="central"
              /* eslint-disable-next-line no-restricted-syntax */
              style={{
                fontSize: 32,
                fontWeight: 500,
                fill: isDisplayValueEmpty ? backgroundColor : 'currentColor',
              }}
            >
              {actualDisplayValue}
            </text>
          )}
        </svg>
      </div>
      {/* Display value to the right (for s size) */}
      {size === 's' && (
        <Text
          className="text-sm ml-[4px]"
          /* eslint-disable-next-line no-restricted-syntax */
          style={isDisplayValueEmpty ? { color: backgroundColor } : undefined}
        >
          {actualDisplayValue}
        </Text>
      )}
    </Stack>
  );
};
