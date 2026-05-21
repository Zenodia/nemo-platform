// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/** Task result shape with metrics and scores for evaluation results. */
interface EvaluationResultTasks {
  [taskName: string]: {
    metrics?: Record<string, { scores?: Record<string, { value?: unknown }> }>;
  };
}

interface MetricWithScore {
  task: string;
  metric: string;
  key: string;
  value: string;
}

export const getMetricsAsList = (tasks?: EvaluationResultTasks): MetricWithScore[] => {
  const metricsAsList: MetricWithScore[] = [];

  if (!tasks) return metricsAsList;

  for (const [taskName, task] of Object.entries(tasks)) {
    const t = task as EvaluationResultTasks[string];
    if (!t?.metrics) continue;

    for (const [metricName, metricValue] of Object.entries(t.metrics)) {
      const mv = metricValue as { scores?: Record<string, { value?: unknown }> };
      if (!mv?.scores) continue;

      for (const [key, valueObj] of Object.entries(mv.scores)) {
        const vo = valueObj as { value?: unknown };
        if (vo?.value == null) continue;

        metricsAsList.push({
          task: taskName,
          metric: metricName,
          key,
          value: String(vo.value).substring(0, 5),
        });
      }
    }
  }

  return metricsAsList;
};
