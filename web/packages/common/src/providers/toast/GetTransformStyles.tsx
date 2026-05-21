// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export const getTransformStyles = ({
  isVisible,
  slideDirection = 'right',
}: {
  isVisible?: boolean;
  slideDirection?: 'top' | 'right' | 'bottom' | 'left';
}) => {
  switch (slideDirection) {
    case 'top':
      return !isVisible ? 'translateY(-100%)' : 'translateY(0)';
    case 'right':
      return !isVisible ? 'translateX(100%)' : 'translateX(0)';
    case 'left':
      return !isVisible ? 'translateX(-100%)' : 'translateX(0)';
    case 'bottom':
    default:
      return !isVisible ? 'translateY(100%)' : 'translateY(0)';
  }
};
