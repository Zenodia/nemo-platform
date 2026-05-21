// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Stack, Text } from '@nvidia/foundations-react-core';
import { Pre } from '@studio/components/common/Pre';
import { ReadOnlyField } from '@studio/components/common/ReadOnlyField';
import { FC } from 'react';

export interface MetricDisplayProps {
  metricName: string;
  metricConfig: {
    type: string;
    params?: Record<string, unknown>;
  };
}

/**
 * Component to display individual metric details.
 * Handles different metric types: string-check, bleu, rouge, em, f1.
 *
 * @param props.metricName - User-defined name for the metric (the key in the metrics object)
 * @param props.metricConfig - Metric configuration containing type and params
 */
export const MetricDisplay: FC<MetricDisplayProps> = ({ metricName, metricConfig }) => {
  const params = metricConfig.params || {};
  const type = metricConfig.type?.toLowerCase() || '';

  return (
    <Stack gap="density-sm">
      <Text kind="label/bold/md">{metricName}</Text>
      <ReadOnlyField label="Type" value={metricConfig.type} />

      {type === 'string-check' && (
        <ReadOnlyField
          label="Check Pattern"
          value={
            params.check ? (
              Array.isArray(params.check) ? (
                <Pre>{params.check.join(',')}</Pre>
              ) : (
                String(params.check)
              )
            ) : (
              '-'
            )
          }
        />
      )}

      {type === 'bleu' && (
        <>
          <ReadOnlyField
            label="References"
            value={params.references ? <Pre>{String(params.references)}</Pre> : '-'}
          />
          {params.candidate && (
            <ReadOnlyField label="Candidate" value={<Pre>{String(params.candidate)}</Pre>} />
          )}
        </>
      )}

      {type === 'rouge' && (
        <>
          <ReadOnlyField
            label="Ground Truth Reference"
            value={params.ground_truth ? <Pre>{String(params.ground_truth)}</Pre> : '-'}
          />
          {params.prediction && (
            <ReadOnlyField label="Prediction" value={<Pre>{String(params.prediction)}</Pre>} />
          )}
        </>
      )}

      {type === 'em' && (
        <>
          <ReadOnlyField
            label="Ground Truth Reference"
            value={params.ground_truth ? <Pre>{String(params.ground_truth)}</Pre> : '-'}
          />
          {params.prediction && (
            <ReadOnlyField label="Prediction" value={<Pre>{String(params.prediction)}</Pre>} />
          )}
        </>
      )}

      {type === 'f1' && (
        <>
          <ReadOnlyField
            label="Ground Truth Reference"
            value={params.ground_truth ? <Pre>{String(params.ground_truth)}</Pre> : '-'}
          />
          {params.prediction && (
            <ReadOnlyField label="Prediction" value={<Pre>{String(params.prediction)}</Pre>} />
          )}
        </>
      )}
    </Stack>
  );
};
