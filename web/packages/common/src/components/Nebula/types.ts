// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export type NebulaColor = 'brand' | 'gold';
export type NebulaShape = 'triangle' | 'sphere';
export type NebulaVariant = 'sphere' | 'ambient';
export type NebulaSizeCategory = 'small' | 'medium' | 'large';

export interface NebulaAppearance {
  color: NebulaColor;
  shape: NebulaShape;
}

export interface NebulaCenter {
  x: number;
  y: number;
}

export interface NebulaCommonProps {
  /** CSS classes to merge with existing root level classes. */
  className?: string;
  /**
   * Color palette for particles.
   * @default "brand"
   */
  color?: NebulaColor;
  /**
   * Particle shape to render.
   * @default "triangle"
   */
  shape?: NebulaShape;
}

export interface NebulaSphereVariant extends NebulaCommonProps {
  /**
   * "sphere" variant has a center point that is positioned automatically
   * within its parent container.
   */
  variant: 'sphere';
  /** X offset from center of nebula sphere. */
  x?: number;
  /** Y offset from center of nebula sphere. */
  y?: number;
  /** Max size that particles will try to conform to when animating. */
  sphereSize?: number;
}

export interface NebulaAmbientVariant extends NebulaCommonProps {
  /** "ambient" variant takes full size of its parent container. */
  variant: 'ambient';
}

export type NebulaProps = NebulaSphereVariant | NebulaAmbientVariant;
