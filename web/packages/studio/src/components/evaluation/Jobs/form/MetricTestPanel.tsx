// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { CodeEditor } from '@nemo/common/src/components/CodeEditor';
import { ContentType } from '@nemo/common/src/components/CodeEditor/constants';
import { TextInputSpinner } from '@nemo/common/src/components/form/TextInputSpinner';
import { LoadingButton } from '@nemo/common/src/components/LoadingButton';
import { UploadModal } from '@nemo/common/src/components/UploadModal';
import type { SubmitUploadType } from '@nemo/common/src/components/UploadModal/types';
import { useToast } from '@nemo/common/src/providers/toast/useToast';
import {
  DEFAULT_MAX_FILE_SAMPLE_ROWS,
  type FileSampleMethod,
} from '@nemo/common/src/utils/sampleTextLines';
import { useEvaluationEvaluateMetric } from '@nemo/sdk/generated/platform/api';
import type { MetricEvaluationResponse } from '@nemo/sdk/generated/platform/schema';
import {
  Banner,
  DropdownHeading,
  DropdownSection,
  Flex,
  SelectContent,
  SelectItem,
  SelectRoot,
  SelectTrigger,
  Stack,
  Text,
} from '@nvidia/foundations-react-core';
import { getErrorMessage } from '@studio/api/common/utils';
import { useDatasetFileContent } from '@studio/api/datasets/useDatasetFileContent';
import { DEFAULT_TEST_DATASET } from '@studio/components/evaluation/Jobs/form/defaults';
import { buildLLMJudgeChatPromptTemplate } from '@studio/components/evaluation/Jobs/form/utils';
import { ResultsLog } from '@studio/components/evaluation/Jobs/TestMetric/ResultsLog';
import {
  cleanScoresObj,
  parseTestDatasetRows,
} from '@studio/components/evaluation/Jobs/TestMetric/utils';
import { FileSamplingMethodSelect } from '@studio/components/FileSamplingSnippet/FileSamplingMethodSelect';
import { FileSamplingSnippet } from '@studio/components/FileSamplingSnippet/FileSamplingSnippet';
import type { MetricPanelFormData } from '@studio/hooks/evaluation/useMetricPanelForm';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { Database, Info, Pencil } from 'lucide-react';
import { type FC, useCallback, useEffect, useRef, useState } from 'react';
import { useController, useForm, useFormContext, useWatch } from 'react-hook-form';

interface PanelFormData {
  dataSource: 'custom' | 'file';
  testDataset: string;
  sampleMethod: FileSampleMethod;
}

interface SelectedDatasetFile {
  workspace: string;
  filesetName: string;
  filePath: string;
}

export interface MetricTestPanelProps {
  /** Called after a test evaluation completes successfully (HTTP OK with a response body). */
  onSuccessfulTestRun?: () => void;
}

export const MetricTestPanel: FC<MetricTestPanelProps> = ({ onSuccessfulTestRun }) => {
  const toast = useToast();
  const workspace = useWorkspaceFromPath();
  const { getValues, control } = useFormContext<MetricPanelFormData>();
  const { mutateAsync: evaluateMetric, isPending } = useEvaluationEvaluateMetric();

  const modelName = useWatch({ control, name: 'body.model.name' });
  const scores = useWatch({ control, name: 'body.scores' });
  const safeScores = scores ?? [];

  const { control: panelControl, setValue: setPanelValue } = useForm<PanelFormData>({
    defaultValues: {
      dataSource: 'custom',
      testDataset: DEFAULT_TEST_DATASET,
      sampleMethod: 'random',
    },
  });

  const { field: testDatasetField } = useController({ control: panelControl, name: 'testDataset' });
  const { field: dataSourceField } = useController({ control: panelControl, name: 'dataSource' });
  const { field: sampleMethodField } = useController({
    control: panelControl,
    name: 'sampleMethod',
  });

  const [results, setResults] = useState<MetricEvaluationResponse | null>(null);
  const [customDataset, setCustomDataset] = useState(DEFAULT_TEST_DATASET);
  const [selectedFile, setSelectedFile] = useState<SelectedDatasetFile | null>(null);
  const [isFilePickerOpen, setIsFilePickerOpen] = useState(false);
  const filePickerSubmittedRef = useRef(false);

  const isFileMode = dataSourceField.value === 'file';

  // Same query key as `FileSamplingSnippet`; TanStack Query deduplicates network requests.
  const { isLoading: isLoadingFileContent, isError: isFileContentError } = useDatasetFileContent({
    workspace: selectedFile?.workspace ?? workspace,
    name: selectedFile?.filesetName ?? '',
    path: selectedFile?.filePath ?? '',
    enabled: Boolean(selectedFile?.filesetName && selectedFile?.filePath),
  });

  useEffect(() => {
    if (!isFileMode || !selectedFile) return;
    setPanelValue('testDataset', '');
  }, [isFileMode, selectedFile, setPanelValue]);

  const handleSampledFileContent = useCallback(
    (text: string) => {
      setPanelValue('testDataset', text);
    },
    [setPanelValue]
  );

  const handleDataSourceChange = (v: string) => {
    if (!isFileMode) {
      setCustomDataset(testDatasetField.value);
    }
    dataSourceField.onChange(v);
    if (v === 'file') {
      setIsFilePickerOpen(true);
    } else {
      setSelectedFile(null);
      setPanelValue('testDataset', customDataset);
    }
  };

  const handleFilePickerClose = () => {
    setIsFilePickerOpen(false);
    if (filePickerSubmittedRef.current) {
      filePickerSubmittedRef.current = false;
      return;
    }
    if (!selectedFile) {
      dataSourceField.onChange('custom');
    }
  };

  const handleFilePickerSubmit = (data: SubmitUploadType) => {
    if (data.type !== 'dataset') {
      return;
    }
    filePickerSubmittedRef.current = true;
    setSelectedFile({
      workspace: data.dataset.workspace,
      filesetName: data.dataset.name,
      filePath: data.path,
    });
    setPanelValue('testDataset', '');
    setIsFilePickerOpen(false);
  };

  const handleCustomDatasetChange = (value: string) => {
    setCustomDataset(value);
    testDatasetField.onChange(value);
  };

  const missingInputs: string[] = [];
  if (!modelName) missingInputs.push('Judge Model');
  if (safeScores.length === 0) missingInputs.push('Score Definitions');

  const canRunTest =
    Boolean(modelName && safeScores.length > 0 && testDatasetField.value.trim()) &&
    !isLoadingFileContent &&
    !(isFileMode && (!selectedFile || isFileContentError));

  const handleRunTest = async () => {
    try {
      const formData = getValues();

      const metric: Record<string, unknown> = {
        type: 'llm-judge',
        model: formData.body.model.name,
        scores: cleanScoresObj(formData.body.scores),
      };
      if (formData.body.description) metric.description = formData.body.description;
      if (formData.body.inference && Object.keys(formData.body.inference).length > 0) {
        metric.inference = formData.body.inference;
      }

      const promptTemplate = buildLLMJudgeChatPromptTemplate(formData.body.messages);
      if (promptTemplate) metric.prompt_template = promptTemplate;

      const rows = parseTestDatasetRows(testDatasetField.value);

      const response = await evaluateMetric({
        workspace,
        data: { metric, dataset: { rows } },
      });

      setResults(response);
      onSuccessfulTestRun?.();
    } catch (error) {
      toast.error(getErrorMessage(error as Error, 'Failed to evaluate metric'));
      setResults(null);
    }
  };

  // The value shown in the source select trigger:
  // - 'custom' → shows "Custom"
  // - 'file' with no file → shows "Dataset File"
  // - 'file' with file selected → uses selectedFile.filePath as value (matched by dynamic SelectItem)
  const sourceSelectValue =
    isFileMode && selectedFile ? selectedFile.filePath : dataSourceField.value;

  return (
    <Stack gap="4" className="overflow-y-auto flex-1">
      {missingInputs.length > 0 && (
        <Banner kind="inline" status="warning">
          Please configure the following options to run the test: {missingInputs.join(', ')}
        </Banner>
      )}

      <Flex gap="2" align="center">
        <SelectRoot
          value={sourceSelectValue}
          onValueChange={(v: string) => {
            if (v === 'custom' || v === 'file') handleDataSourceChange(v);
            // selectedFile.filePath clicks are no-ops (already selected)
          }}
        >
          <SelectTrigger
            className="flex-1 overflow-hidden"
            placeholder="Select source..."
            slotStart={
              isFileMode ? <Database size={14} aria-hidden /> : <Pencil size={14} aria-hidden />
            }
            slotEnd={isLoadingFileContent ? <TextInputSpinner /> : undefined}
            renderValue={(v: string | string[] | undefined) => {
              const valueStr = Array.isArray(v) ? v[0] : v;
              if (valueStr == null || valueStr === '') return null;
              if (valueStr === 'custom') {
                return (
                  <Text kind="body/regular/md" className="truncate">
                    Custom
                  </Text>
                );
              }
              if (valueStr === 'file') {
                return (
                  <Text kind="body/regular/md" className="truncate">
                    {selectedFile ? 'Select different file...' : 'Dataset File'}
                  </Text>
                );
              }
              return (
                <Text kind="body/regular/md" className="truncate" title={valueStr}>
                  {valueStr}
                </Text>
              );
            }}
          />
          <SelectContent>
            {isFileMode && selectedFile && (
              <SelectItem value={selectedFile.filePath}>{selectedFile.filePath}</SelectItem>
            )}
            <DropdownSection>
              <DropdownHeading>Load Test Cases</DropdownHeading>
              <SelectItem
                value="custom"
                slotStart={<Pencil aria-hidden className="size-4 shrink-0 text-secondary" />}
              >
                Custom
              </SelectItem>
              <SelectItem
                value="file"
                slotStart={<Database aria-hidden className="size-4 shrink-0 text-secondary" />}
              >
                {selectedFile ? 'Select different file...' : 'Dataset File'}
              </SelectItem>
            </DropdownSection>
          </SelectContent>
        </SelectRoot>

        {isFileMode && selectedFile && (
          <FileSamplingMethodSelect
            value={sampleMethodField.value}
            onValueChange={sampleMethodField.onChange}
          />
        )}

        <LoadingButton
          type="button"
          kind="secondary"
          disabled={!canRunTest || isPending}
          loading={isPending}
          onClick={handleRunTest}
        >
          Run Test
        </LoadingButton>
      </Flex>

      {isFileMode && selectedFile ? (
        <FileSamplingSnippet
          workspace={selectedFile.workspace}
          filesetName={selectedFile.filesetName}
          filePath={selectedFile.filePath}
          maxSampleRows={DEFAULT_MAX_FILE_SAMPLE_ROWS}
          sampleMethod={sampleMethodField.value}
          onSampledContentChange={handleSampledFileContent}
          slotFooter={
            <Flex gap="density-xs" align="center" className="text-secondary">
              <Info size={12} className="shrink-0" />
              <Text kind="label/regular/sm">
                Live evaluation is limited to {DEFAULT_MAX_FILE_SAMPLE_ROWS} rows. Use it for
                testing and debugging, then run jobs for larger datasets.
              </Text>
            </Flex>
          }
        />
      ) : (
        <>
          <CodeEditor
            content={testDatasetField.value}
            contentType={ContentType.JSONL}
            onChange={handleCustomDatasetChange}
            className="min-h-[200px] max-h-[400px]"
            hideCopyButton
          />

          <Flex gap="density-xs" align="center" className="text-secondary">
            <Info size={12} className="shrink-0" />
            <Text kind="label/regular/sm">
              Live evaluation is limited to {DEFAULT_MAX_FILE_SAMPLE_ROWS} rows. Use it for testing
              and debugging, then run jobs for larger datasets.
            </Text>
          </Flex>
        </>
      )}

      {results && <ResultsLog results={results} />}

      <UploadModal
        workspace={workspace}
        open={isFilePickerOpen}
        onClose={handleFilePickerClose}
        includeDataset
        title="Select Dataset File"
        submitButtonText="Select"
        onSubmit={handleFilePickerSubmit}
      />
    </Stack>
  );
};
