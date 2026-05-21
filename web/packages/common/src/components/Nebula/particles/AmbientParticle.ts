// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Particle } from '@nemo/common/src/components/Nebula/particles/Base';
import type { NebulaAppearance } from '@nemo/common/src/components/Nebula/types';

export class AmbientParticle extends Particle {
  canvas: HTMLCanvasElement;
  spinAngle = 0;
  x = 0;
  y = 0;
  driftVelocityX: number;
  driftVelocityY: number;
  prevCanvasSize = '';

  constructor(canvas: HTMLCanvasElement, appearance: NebulaAppearance) {
    super(appearance);
    this.canvas = canvas;
    this.driftVelocityX = this.randomFloat(-0.3, 0.3);
    this.driftVelocityY = this.randomFloat(-0.3, 0.3);
    this.setPosition();
  }

  setPosition(): void {
    this.prevCanvasSize = `${this.canvas.width}x${this.canvas.height}`;
    this.x = this.randomFloat(0, this.canvas.width);
    this.y = this.randomFloat(0, this.canvas.height);
  }

  update(): void {
    if (this.prevCanvasSize !== `${this.canvas.width}x${this.canvas.height}`) {
      this.setPosition();
      return;
    }
    this.x += this.driftVelocityX;
    this.y += this.driftVelocityY;
    if (this.x < 0 || this.x > this.canvas.width) this.driftVelocityX *= -1;
    if (this.y < 0 || this.y > this.canvas.height) this.driftVelocityY *= -1;
    this.spinAngle += this.spinSpeed;
  }
}
