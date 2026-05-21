// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { parseFilesetLocation } from '@nemo/common/src/components/DatasetFileSelect/parseFilesetLocation';
import type { VariableDef } from '@nemo/common/src/components/form/VariableTextArea';
import { Banner, Flex, Panel, Spinner, Stack, Text } from '@nvidia/foundations-react-core';
import { datasetFileContentQueryOptions } from '@studio/api/datasets/useDatasetFileContent';
import {
  getMetricRunTemplateFieldValidation,
  type MetricRunFileValidationResult,
  validateMetricRunFileContent,
} from '@studio/components/sidePanels/MetricRunSidePanel/FileValidationPanel/utils';
import type { MetricRunSidePanelFormData } from '@studio/components/sidePanels/MetricRunSidePanel/types';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, CheckCircle2, CircleHelp } from 'lucide-react';
import { type FC, type ReactNode, useEffect, useMemo, useState } from 'react';

export interface FileValidationPanelProps {
  dataset: string | null;
  jobType: MetricRunSidePanelFormData['jobType'];
  promptTemplate: string;
  workspace: string;
  onVariablesChange?: (variables: VariableDef[]) => void;
}

const formatLabel = (format: MetricRunFileValidationResult['format']): string =>
  format ? format.toUpperCase() : 'File';

const formatRowCount = (rowCount: number | undefined): string => {
  if (rowCount === undefined) return 'Rows detected';
  return `${rowCount.toLocaleString()} ${rowCount === 1 ? 'row' : 'rows'} detected`;
};

const StatusRow: FC<{ icon: ReactNode; children: ReactNode }> = ({ icon, children }) => (
  <Flex gap="density-md" align="center">
    {icon}
    <Text kind="body/regular/md">{children}</Text>
  </Flex>
);

const SuccessIcon = <CheckCircle2 size={16} className="text-feedback-success shrink-0" />;
const WarningIcon = <AlertTriangle size={16} className="text-feedback-warning shrink-0" />;
const HelpIcon = <CircleHelp size={16} className="text-secondary shrink-0" />;

export const FileValidationPanel: FC<FileValidationPanelProps> = ({
  dataset,
  jobType,
  promptTemplate,
  workspace,
  onVariablesChange,
}) => {
  const parsedDataset = useMemo(
    () => (dataset ? parseFilesetLocation(dataset, workspace) : null),
    [dataset, workspace]
  );
  const [validationResult, setValidationResult] = useState<MetricRunFileValidationResult | null>(
    null
  );
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  const datasetContentQuery = useQuery({
    ...datasetFileContentQueryOptions({
      workspace: parsedDataset?.workspace ?? workspace,
      name: parsedDataset?.name ?? '',
      path: parsedDataset?.objectPath ?? '',
    }),
    enabled: !!parsedDataset?.objectPath,
  });

  const variables = useMemo<VariableDef[]>(() => {
    if (!validationResult?.isValid) return [];
    return validationResult.rootKeys.map((key) => ({
      name: key,
      description: 'Dataset field',
    }));
  }, [validationResult]);

  useEffect(() => {
    onVariablesChange?.(variables);
  }, [onVariablesChange, variables]);

  useEffect(() => {
    let isCurrent = true;

    if (!parsedDataset?.objectPath || datasetContentQuery.data == null) {
      setValidationResult(null);
      setValidationError(null);
      setIsValidating(false);
      return () => {
        isCurrent = false;
      };
    }

    setIsValidating(true);
    setValidationError(null);

    validateMetricRunFileContent({
      content: datasetContentQuery.data,
      path: parsedDataset.objectPath,
      promptTemplate: '',
      jobType,
    })
      .then((result) => {
        if (!isCurrent) return;
        setValidationResult(result);
      })
      .catch((error: unknown) => {
        if (!isCurrent) return;
        setValidationResult(null);
        setValidationError(error instanceof Error ? error.message : 'Failed to validate file');
      })
      .finally(() => {
        if (isCurrent) setIsValidating(false);
      });

    return () => {
      isCurrent = false;
    };
  }, [datasetContentQuery.data, jobType, parsedDataset?.objectPath]);

  if (!dataset) return null;

  if (!parsedDataset?.objectPath) {
    return (
      <Banner status="error" kind="inline">
        Unable to validate the selected dataset file.
      </Banner>
    );
  }

  if (datasetContentQuery.isLoading || isValidating) {
    return (
      <Banner status="info" kind="inline">
        <Flex gap="density-sm" align="center">
          <Spinner size="small" aria-label="Validating file" />
          Validating file format and structure...
        </Flex>
      </Banner>
    );
  }

  if (datasetContentQuery.error || validationError) {
    return (
      <Banner status="error" kind="inline">
        File validation failed:{' '}
        {validationError ?? datasetContentQuery.error?.message ?? 'Unable to load file content'}
      </Banner>
    );
  }

  if (!validationResult) return null;

  if (!validationResult.isValid) {
    return (
      <Banner status="error" kind="inline">
        File validation failed: {validationResult.error ?? 'Invalid file content'}
      </Banner>
    );
  }

  const schemaType = validationResult.detectionResult?.schemaType;
  const { templateFields, missingTemplateFields } = getMetricRunTemplateFieldValidation(
    promptTemplate,
    validationResult.rootKeys
  );
  const hasTemplateFields = templateFields.length > 0;

  return (
    <Panel elevation="high">
      <Stack gap="density-md">
        <Text kind="label/bold/md">File Validation</Text>

        <StatusRow icon={SuccessIcon}>{formatLabel(validationResult.format)} is valid</StatusRow>

        <StatusRow icon={SuccessIcon}>{formatRowCount(validationResult.rowCount)}</StatusRow>

        <StatusRow icon={schemaType ? SuccessIcon : HelpIcon}>
          {schemaType ? `Detected Schema: ${schemaType}` : 'Schema could not be auto-detected'}
        </StatusRow>

        {hasTemplateFields && (
          <StatusRow icon={missingTemplateFields.length > 0 ? WarningIcon : SuccessIcon}>
            {missingTemplateFields.length > 0
              ? `Prompt template fields missing from dataset: ${missingTemplateFields.join(', ')}`
              : 'All prompt template fields detected'}
          </StatusRow>
        )}

        {jobType === 'online' && !hasTemplateFields && (
          <StatusRow icon={HelpIcon}>Add a prompt template to validate dataset fields</StatusRow>
        )}
      </Stack>
    </Panel>
  );
};
