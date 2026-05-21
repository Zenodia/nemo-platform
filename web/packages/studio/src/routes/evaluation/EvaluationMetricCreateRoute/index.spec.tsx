// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ROUTE_PARAMS } from '@studio/constants/routes';
import { workspace1 } from '@studio/mocks/entity-store/projects';
import { EvaluationMetricCreateRoute } from '@studio/routes/evaluation/EvaluationMetricCreateRoute';
import { mockUseParams } from '@studio/tests/util/mockUseParams';
import { renderRoute } from '@studio/tests/util/render';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useFormContext, useWatch } from 'react-hook-form';

const { mockCreateMetric, mockUseJudgeModels } = vi.hoisted(() => ({
  mockCreateMetric: vi.fn(),
  mockUseJudgeModels: vi.fn(),
}));

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
    useEvaluationCreateMetric: vi.fn(() => ({
      mutateAsync: mockCreateMetric,
      isPending: false,
    })),
    useEvaluationEvaluateMetric: vi.fn(() => ({
      mutateAsync: vi.fn(),
      isPending: false,
    })),
  };
});

describe('EvaluationJobCreateRoute', () => {
  beforeEach(() => {
    mockUseParams({
      [ROUTE_PARAMS.workspace]: workspace1.name,
    });
    mockCreateMetric.mockReset();
    mockCreateMetric.mockResolvedValue({});
    mockUseJudgeModels.mockReturnValue({
      data: [],
      isLoading: false,
      error: undefined,
    });
  });

  describe('Success State', () => {
    it('should render form panel with heading and key sections', async () => {
      renderRoute(<EvaluationMetricCreateRoute />);

      // Wait for form to render - the Metric component renders "New Evaluation Metric"
      await waitFor(() => {
        expect(screen.getByText('New Evaluation Metric')).toBeInTheDocument();
      });

      // Key sections of the metric form
      expect(screen.getByText('Metric Type')).toBeInTheDocument();
      expect(screen.getByText('Score Definitions')).toBeInTheDocument();

      // Submit button
      expect(screen.getByRole('button', { name: 'Save Evaluation Metric' })).toBeInTheDocument();
    });

    it('creates LLM judge metrics with a chat prompt template', async () => {
      const user = userEvent.setup();
      renderRoute(<EvaluationMetricCreateRoute />);

      await user.type(screen.getByRole('textbox', { name: 'Metric Name' }), 'my-metric');
      await user.type(await screen.findByTestId('judge-model-input'), 'workspace-a/judge-model');
      await user.click(screen.getByRole('button', { name: 'Save Evaluation Metric' }));
      await user.click(await screen.findByRole('button', { name: 'Save' }));

      await waitFor(() => {
        expect(mockCreateMetric).toHaveBeenCalledOnce();
      });

      expect(mockCreateMetric).toHaveBeenCalledWith(
        expect.objectContaining({
          workspace: workspace1.name,
          data: expect.objectContaining({
            type: 'llm-judge',
            model: 'workspace-a/judge-model',
            prompt_template: expect.objectContaining({
              messages: [
                expect.objectContaining({ role: 'system' }),
                expect.objectContaining({ role: 'user' }),
              ],
            }),
          }),
        })
      );

      const createMetricRequest = mockCreateMetric.mock.calls[0][0] as {
        data: Record<string, unknown>;
      };
      expect(typeof createMetricRequest.data.prompt_template).toBe('object');
      expect(createMetricRequest.data).not.toHaveProperty('system_prompt');
    });
  });

  describe('Form Sections', () => {
    it('should render judge model and score definitions sections', async () => {
      renderRoute(<EvaluationMetricCreateRoute />);

      // Wait for form to render
      await screen.findByText('New Evaluation Metric');

      // Judge Model and Prompt Template sections
      expect(screen.getAllByText('Judge Model').length).toBeGreaterThan(0);
      expect(screen.getByText('Model & Prompt')).toBeInTheDocument();
      expect(screen.getByText('Score Definitions')).toBeInTheDocument();
    });
  });

  describe('Page Title', () => {
    it('should set accessible title with project name', async () => {
      renderRoute(<EvaluationMetricCreateRoute />);

      await waitFor(() => {
        expect(screen.getByText('New Evaluation Metric')).toBeInTheDocument();
      });

      expect(document.title).toContain(workspace1.name);
    });
  });
});
