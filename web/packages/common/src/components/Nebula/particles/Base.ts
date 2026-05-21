// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type {
  NebulaAppearance,
  NebulaColor,
  NebulaShape,
  NebulaSizeCategory,
} from '@nemo/common/src/components/Nebula/types';

const COLOR_SETS: Record<NebulaColor, Record<NebulaSizeCategory, string>> = {
  brand: {
    small: 'rgba(255, 255, 255, 0.3)',
    medium: 'rgba(87, 146, 16, 0.4)',
    large: 'rgba(118, 185, 0, 0.5)',
  },
  gold: {
    small: 'rgba(255, 255, 255, 0.3)',
    medium: 'rgba(223, 181, 95, 1)',
    large: 'rgba(223, 181, 95, 1)',
  },
};

const RADIUS_RANGES: Record<
  NebulaShape,
  Record<NebulaSizeCategory, { min: number; max: number }>
> = {
  triangle: {
    small: { min: 1, max: 2 },
    medium: { min: 2, max: 3 },
    large: { min: 3, max: 4 },
  },
  sphere: {
    small: { min: 1, max: 2 },
    medium: { min: 2, max: 3 },
    large: { min: 2.5, max: 3.5 },
  },
};

export abstract class Particle {
  appearance: NebulaAppearance;
  radiusSeed: number;
  sizeCategory: NebulaSizeCategory;
  spinSpeed: number;
  radius: number;
  color: string;
  abstract x: number;
  abstract y: number;
  abstract spinAngle: number;

  constructor(appearance: NebulaAppearance) {
    this.appearance = appearance;
    this.radiusSeed = Math.random();
    const { sizeCategory, spinSpeed } = this.getSizeCategoryAndSpin();
    this.sizeCategory = sizeCategory;
    this.spinSpeed = spinSpeed;
    this.radius = this.computeRadiusForShape(appearance.shape);
    this.color = this.getColorForScheme(appearance.color, sizeCategory);
  }

  setAppearance(appearance: NebulaAppearance): void {
    const shapeChanged = appearance.shape !== this.appearance.shape;
    const colorChanged = appearance.color !== this.appearance.color;
    this.appearance = appearance;
    if (colorChanged) {
      this.color = this.getColorForScheme(appearance.color, this.sizeCategory);
    }
    if (shapeChanged) {
      this.radius = this.computeRadiusForShape(appearance.shape);
      this.onShapeChange();
    }
  }

  onShapeChange(): void {}

  abstract update(sphereSize: number): void;

  draw(c: CanvasRenderingContext2D): void {
    c.save();
    c.translate(this.x, this.y);
    c.rotate(this.spinAngle);
    c.beginPath();
    if (this.appearance.shape === 'sphere') {
      c.arc(0, 0, this.radius, 0, 2 * Math.PI);
    } else {
      c.moveTo(0, -this.radius);
      c.lineTo(-this.radius, this.radius);
      c.lineTo(this.radius, this.radius);
    }
    c.closePath();
    c.fillStyle = this.color;
    c.fill();
    c.restore();
  }

  protected randomFloat(min: number, max: number): number {
    return Math.random() * (max - min) + min;
  }

  private getSizeCategoryAndSpin(): { sizeCategory: NebulaSizeCategory; spinSpeed: number } {
    const rand = Math.random();
    if (rand < 0.7) {
      return { sizeCategory: 'small', spinSpeed: this.randomFloat(0.05, 0.1) };
    }
    if (rand < 0.9) {
      return { sizeCategory: 'medium', spinSpeed: this.randomFloat(0.03, 0.08) };
    }
    return { sizeCategory: 'large', spinSpeed: this.randomFloat(0.01, 0.04) };
  }

  protected computeRadiusForShape(shape: NebulaShape): number {
    const { min, max } = RADIUS_RANGES[shape][this.sizeCategory];
    return min + this.radiusSeed * (max - min);
  }

  private getColorForScheme(color: NebulaColor, sizeCategory: NebulaSizeCategory): string {
    return COLOR_SETS[color][sizeCategory];
  }
}
