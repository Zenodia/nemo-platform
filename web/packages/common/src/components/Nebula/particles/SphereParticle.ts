// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Particle } from '@nemo/common/src/components/Nebula/particles/Base';
import type { NebulaAppearance, NebulaCenter } from '@nemo/common/src/components/Nebula/types';

export class SphereParticle extends Particle {
  center: NebulaCenter;
  spinAngle = 0;
  x: number;
  y: number;
  orbitVelocity = 1e-3;
  radians = Math.random() * Math.PI * 2;
  originalDistance: { x: number; y: number };
  distanceFromCenter: { x: number; y: number };
  originalRadius: number;

  constructor(center: NebulaCenter, scaleFactor: number, appearance: NebulaAppearance) {
    super(appearance);
    this.center = center;
    this.x = center.x;
    this.y = center.y;
    this.originalDistance = {
      x: this.randomFloat(40, 70) * scaleFactor,
      y: this.randomFloat(40, 70) * scaleFactor,
    };
    this.distanceFromCenter = { ...this.originalDistance };
    this.originalRadius = this.radius;
  }

  update(sphereSize: number): void {
    this.radius = Math.min(this.originalRadius, this.originalRadius * (sphereSize / 15));
    this.radians += this.orbitVelocity;
    this.x = this.center.x + Math.cos(this.radians) * this.distanceFromCenter.x;
    this.y = this.center.y + Math.sin(this.radians) * this.distanceFromCenter.y;
    this.spinAngle += this.spinSpeed;
  }

  scaleOrbit(center: NebulaCenter, scaleFactor: number): void {
    this.center = center;
    this.originalDistance.x *= scaleFactor;
    this.originalDistance.y *= scaleFactor;
    this.distanceFromCenter.x = this.originalDistance.x;
    this.distanceFromCenter.y = this.originalDistance.y;
  }

  override onShapeChange(): void {
    this.originalRadius = this.radius;
  }
}
