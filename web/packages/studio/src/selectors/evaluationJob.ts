// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type {
  MetricEvaluationJob,
  BenchmarkEvaluationJob,
  PlatformJobStatus,
} from '@nemo/sdk/generated/platform/schema';

// Union type for V2 evaluation jobs
export type EvaluationJobV2 = MetricEvaluationJob | BenchmarkEvaluationJob;

export const getEvaluationJobId = (job: EvaluationJobV2) => {
  return job.id;
};

export const getEvaluationJobName = (job: EvaluationJobV2) => {
  return job.name;
};

// Extract model from job spec
export const getEvaluationJobModel = (job: EvaluationJobV2): string | undefined => {
  const spec = job.spec;
  if (!spec) return undefined;

  // Check different spec types for model field
  if ('model' in spec) {
    // Model can be EvaluatorModel (object) or ModelRef (string)
    const model = spec.model;
    if (typeof model === 'string') return model;
    return model?.name;
  }

  return undefined;
};

// Extract config/metric/benchmark reference from job spec
// For MetricEvaluationJob, returns the metric reference
// For BenchmarkEvaluationJob, returns the benchmark reference
export const getEvaluationJobConfigRef = (job: EvaluationJobV2): string | undefined => {
  const spec = job.spec;
  if (!spec) return undefined;

  // Metric jobs have metric field
  if ('metric' in spec) {
    const metric = spec.metric;
    // If metric is a string (MetricRef), return it
    if (typeof metric === 'string') {
      return metric;
    }
    // Inline metrics don't have a reference
    return undefined;
  }

  // Benchmark jobs have benchmark field
  if ('benchmark' in spec) {
    return spec.benchmark as string;
  }

  return undefined;
};

export const getEvaluationJobCustomFields = (job: EvaluationJobV2) => {
  return Object.keys(job?.custom_fields || {}) || [];
};

// Status checks
export const isEvaluationJobCreated = (status: PlatformJobStatus | undefined) => {
  return status === 'created';
};

export const isEvaluationJobSucceeded = (status: PlatformJobStatus | undefined) => {
  return status === 'completed';
};

export const isEvaluationJobInProgress = (status: PlatformJobStatus | undefined) => {
  return status === 'active';
};

// Extract model/target from job spec
// This replaces the old getEvaluationJobTarget which was for V1 jobs
export const getEvaluationJobTarget = (job: EvaluationJobV2) => {
  const spec = job.spec;
  if (!spec) return undefined;

  // Check different spec types for model field
  if ('model' in spec) {
    return spec.model;
  }

  return undefined;
};
