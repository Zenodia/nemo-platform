// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Button, Card, Flex, Text } from '@nvidia/foundations-react-core';
import { TooltipCoords } from '@studio/components/WelcomeTour/types';
import { computePosition } from '@studio/components/WelcomeTour/utils';
import { X } from 'lucide-react';
import { useTour } from 'modern-tour';
import { FC, useLayoutEffect, useRef, useState } from 'react';

interface TourTooltipProps {
  onClose: () => void;
}

export const TourTooltip: FC<TourTooltipProps> = ({ onClose }) => {
  const { step, currentStep, totalSteps, targetRect, next, prev } = useTour();
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [coords, setCoords] = useState<TooltipCoords | null>(null);

  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === totalSteps - 1;

  useLayoutEffect(() => {
    if (!tooltipRef.current || !targetRect || !step) {
      setCoords(null);
      return;
    }
    const rect = tooltipRef.current.getBoundingClientRect();
    setCoords(computePosition(targetRect, rect, step.position ?? 'bottom'));
  }, [targetRect, step, currentStep]);

  if (!step || !targetRect) return null;

  return (
    <div
      ref={tooltipRef}
      className={`fixed z-[10000] w-[360px] max-w-[calc(100vw-32px)] ${coords ? '' : 'invisible'}`}
      style={coords ? { left: coords.left, top: coords.top } : undefined} // eslint-disable-line no-restricted-syntax
    >
      <Card
        className="relative h-fit bg-surface-base shadow-lg"
        slotHeader={
          <h2 className="nv-modal-heading">{typeof step.title === 'string' ? step.title : ''}</h2>
        }
      >
        <Button
          aria-label="Close"
          kind="tertiary"
          color="neutral"
          size="medium"
          className="absolute top-3 right-3"
          onClick={onClose}
        >
          <X />
        </Button>
        {step.content && (
          <Text kind="label/regular/md" className="whitespace-normal break-words" lineHeight="125">
            {step.content}
          </Text>
        )}
        <Flex justify="between" align="center" className="mt-3">
          <Text kind="label/regular/sm" className="text-tertiary">
            {currentStep + 1} of {totalSteps}
          </Text>
          <Flex gap="density-sm">
            {isFirstStep && (
              <Button kind="tertiary" color="neutral" size="small" onClick={onClose}>
                Skip
              </Button>
            )}
            {!isFirstStep && (
              <Button kind="secondary" color="neutral" size="small" onClick={prev}>
                Back
              </Button>
            )}
            <Button kind="primary" color="brand" size="small" onClick={isLastStep ? onClose : next}>
              {isLastStep ? 'Done' : 'Next'}
            </Button>
          </Flex>
        </Flex>
      </Card>
    </div>
  );
};
