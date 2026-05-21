// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ModelEntity } from '@nemo/sdk/generated/platform/schema';
import { MetricFormPanels } from '@studio/components/evaluation/Jobs/form/MetricFormPanels';
import { DEFAULT_BUILD_MODEL_NAME } from '@studio/constants/constants';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { workspace1 } from '@studio/mocks/entity-store/projects';
import { mockUseParams } from '@studio/tests/util/mockUseParams';
import { renderRoute } from '@studio/tests/util/render';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useFormContext, useWatch } from 'react-hook-form';

const mockUseJudgeModels = vi.hoisted(() =>
  vi.fn(() => ({
    data: [] as ModelEntity[],
    isLoading: false,
    error: undefined as Error | undefined,
  }))
);

vi.mock('@studio/components/evaluation/JudgeModelSelect', () => ({
  JudgeModelSelect: ({ formFieldName }: { formFieldName: string }) => {
    const { control, setValue } = useFormContext();
    const value = useWatch({ control, name: formFieldName as never }) as unknown as
      | string
      | undefined;
    return (
      <div>
        <label htmlFor="judge-model-input">Judge Model</label>
        <input
          id="judge-model-input"
          data-testid="judge-model-input"
          value={value ?? ''}
          onChange={(e) => setValue(formFieldName as never, e.target.value as never)}
        />
      </div>
    );
  },
}));

vi.mock('@studio/hooks/evaluation/useJudgeModels', () => ({
  useJudgeModels: mockUseJudgeModels,
}));

vi.mock('@nemo/sdk/generated/platform/api', async (importOriginal) => {
  const original = await importOriginal<typeof import('@nemo/sdk/generated/platform/api')>();
  return {
    ...original,
    useEvaluationEvaluateMetric: vi.fn(() => ({
      mutateAsync: vi.fn(),
      isPending: false,
    })),
  };
});

const TEST_FORM_ID = 'metric-form';

const renderPanel = (onSubmit = vi.fn()) =>
  renderRoute(
    <>
      <MetricFormPanels onSubmit={onSubmit} formId={TEST_FORM_ID} />
      <button type="submit" form={TEST_FORM_ID}>
        Save Metric
      </button>
    </>
  );

describe('MetricFormPanels', () => {
  beforeEach(() => {
    mockUseParams({ [ROUTE_PARAMS.workspace]: workspace1.name });
    mockUseJudgeModels.mockReturnValue({
      data: [],
      isLoading: false,
      error: undefined,
    });
  });

  describe('Left panel', () => {
    it('renders metric name, description, metric type, and score sections', async () => {
      renderPanel();

      // KUI renders the label text in multiple elements; check at least one exists
      expect((await screen.findAllByText('Metric Name')).length).toBeGreaterThan(0);
      expect(screen.getByText('Metric Type')).toBeInTheDocument();
      expect(screen.getByText('Score Definitions')).toBeInTheDocument();
      expect(screen.getByText('LLM-as-a-Judge')).toBeInTheDocument();
    });
  });

  describe('Default judge model', () => {
    it('prefills judge model when the workspace lists the default build model', async () => {
      const expectedUrn = `${workspace1.name}/${DEFAULT_BUILD_MODEL_NAME}`;
      mockUseJudgeModels.mockReturnValue({
        data: [
          {
            id: 'model-default-build',
            workspace: workspace1.name,
            name: DEFAULT_BUILD_MODEL_NAME,
            created_at: '2024-01-01T00:00:00.000Z',
            updated_at: '2024-01-01T00:00:00.000Z',
            api_endpoint: { url: 'https://example.com/v1/chat/completions', format: 'nim' },
          },
        ],
        isLoading: false,
        error: undefined,
      });

      renderPanel();

      await waitFor(() => {
        expect(screen.getByTestId('judge-model-input')).toHaveValue(expectedUrn);
      });
    });

    it('does not prefill judge model when the default build model is not in the list', async () => {
      mockUseJudgeModels.mockReturnValue({
        data: [
          {
            id: 'model-other',
            workspace: workspace1.name,
            name: 'some-other-model',
            created_at: '2024-01-01T00:00:00.000Z',
            updated_at: '2024-01-01T00:00:00.000Z',
            api_endpoint: { url: 'https://example.com/v1/chat/completions', format: 'nim' },
          },
        ],
        isLoading: false,
        error: undefined,
      });

      renderPanel();

      await screen.findByTestId('judge-model-input');
      expect(screen.getByTestId('judge-model-input')).toHaveValue('');
    });
  });

  describe('Right panel tabs', () => {
    it('shows Configure tab content by default', async () => {
      renderPanel();

      // KUI SegmentedControl renders items as role="radio" inside a radiogroup
      expect(await screen.findByRole('radio', { name: 'Configure' })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: 'Test' })).toBeInTheDocument();
      expect(screen.getByText('Model & Prompt')).toBeInTheDocument();
    });

    it('switches to Test tab and shows test panel', async () => {
      const user = userEvent.setup();
      renderPanel();

      await screen.findByRole('radio', { name: 'Test' });
      await user.click(screen.getByRole('radio', { name: 'Test' }));

      await waitFor(() => {
        expect(screen.getByText('Run Test')).toBeInTheDocument();
      });
    });
  });

  it('requires confirmation again after editing a successfully tested metric', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderPanel(onSubmit);

    await user.type(screen.getByRole('textbox', { name: 'Metric Name' }), 'response-quality');
    await user.type(await screen.findByTestId('judge-model-input'), 'test-model');
    await user.click(screen.getByRole('radio', { name: 'Test' }));
    await user.click(await screen.findByRole('button', { name: 'Run Test' }));

    await user.click(screen.getByRole('button', { name: 'Save Metric' }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledTimes(1);
    });
    expect(screen.queryByText('Save without Testing?')).not.toBeInTheDocument();

    await user.click(screen.getByRole('radio', { name: 'Configure' }));
    await user.type(screen.getByTestId('judge-model-input'), '-edited');
    await user.click(screen.getByRole('button', { name: 'Save Metric' }));

    expect(await screen.findByText('Save without Testing?')).toBeInTheDocument();
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });
});
