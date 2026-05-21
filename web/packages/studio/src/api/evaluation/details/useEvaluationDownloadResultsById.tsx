// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ExcludedChatCompletionMessageParam } from '@nemo/common/src/types/chat';
import { evaluationDownloadMetricJobResultRowScores } from '@nemo/sdk/generated/platform/api';
import { useQuery } from '@tanstack/react-query';

export interface EvaluationMetrics {
  bleu?: {
    scores?: {
      sentence?: {
        value: number;
      };
    };
  };
  [key: string]: unknown;
}

export type EvaluationItem =
  | {
      prompt: string;
      ideal_response: string;
    }
  | {
      messages: ExcludedChatCompletionMessageParam[];
    };

export interface EvaluationSample {
  output_text: string;
}
export interface EvaluationResultItem {
  item: EvaluationItem;
  sample: EvaluationSample;
  metrics: EvaluationMetrics;
}

// V2 row score shape from the platform API
interface V2RowScore {
  index: number;
  row: Record<string, unknown>;
  scores?: Record<string, number>;
  error?: string;
}

// Map V2 row scores to the EvaluationResultItem format used by the UI
function mapV2RowScores(rows: V2RowScore[]): EvaluationResultItem[] {
  return rows.map((row) => ({
    item: {
      prompt: String(row.row?.prompt ?? row.row?.input ?? ''),
      ideal_response: String(row.row?.ideal_response ?? row.row?.reference ?? ''),
      ...(row.row?.messages
        ? { messages: row.row.messages as ExcludedChatCompletionMessageParam[] }
        : {}),
    } as EvaluationItem,
    sample: {
      output_text: String(row.row?.output ?? row.row?.output_text ?? ''),
    },
    metrics: mapV2Scores(row.scores),
  }));
}

function mapV2Scores(scores?: Record<string, number>): EvaluationMetrics {
  if (!scores) return {};

  const result: EvaluationMetrics = {};

  // Map V2 flat scores to the nested metrics structure the UI expects
  for (const [key, value] of Object.entries(scores)) {
    if (key === 'sentence' || key === 'corpus') {
      // BLEU sub-scores
      if (!result.bleu) {
        result.bleu = { scores: {} };
      }
      if (!result.bleu!.scores) {
        result.bleu!.scores = {};
      }
      (result.bleu!.scores as Record<string, { value: number }>)[key] = { value };
    } else {
      result[key] = value;
    }
  }

  return result;
}

async function fetchEvaluationResultsV2(
  workspace: string,
  jobName: string
): Promise<EvaluationResultItem[]> {
  const blob = await evaluationDownloadMetricJobResultRowScores(workspace, jobName);

  const text = await blob.text();
  const parsed = JSON.parse(text);

  // The response is either an array of row scores or wrapped in a container
  const rows: V2RowScore[] = Array.isArray(parsed)
    ? parsed
    : (parsed.data ?? parsed.row_scores ?? []);

  return mapV2RowScores(rows);
}

export const useEvaluationDownloadResultsById = (workspace: string, jobName: string) => {
  return useQuery<EvaluationResultItem[], Error>({
    queryKey: ['evaluationDownloadResults', workspace, jobName],
    queryFn: () => fetchEvaluationResultsV2(workspace, jobName),
    enabled: !!workspace && !!jobName,
  });
};
