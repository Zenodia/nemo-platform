// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MetricSelector } from '@studio/components/evaluation/Jobs/form/MetricSelector';
import { render, screen } from '@testing-library/react';
import { FormProvider, useForm } from 'react-hook-form';

function TestWrapper({ children }: { children: React.ReactNode }) {
  const methods = useForm();
  return <FormProvider {...methods}>{children}</FormProvider>;
}

describe('MetricSelector', () => {
  it('should render without crashing when no metric type is selected', () => {
    const { container } = render(
      <TestWrapper>
        <MetricSelector workspace="default" />
      </TestWrapper>
    );

    expect(container).toBeInTheDocument();
  });

  it('should show LLM-as-a-Judge form fields when llm-judge type is selected', () => {
    const Wrapper = () => {
      const methods = useForm({
        defaultValues: {
          metricType: 'llm-judge',
          metricConfig: {},
        },
      });
      return (
        <FormProvider {...methods}>
          <MetricSelector workspace="default" />
        </FormProvider>
      );
    };

    render(<Wrapper />);

    // Verify required form fields are displayed
    expect(screen.getByLabelText(/Score Name/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Minimum Value/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Maximum Value/)).toBeInTheDocument();

    // Verify optional fields
    expect(screen.getByLabelText(/Score Description/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Prompt Template/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Parser Pattern/)).toBeInTheDocument();
  });

  it('should display required field markers for LLM-as-a-Judge', () => {
    const Wrapper = () => {
      const methods = useForm({
        defaultValues: {
          metricType: 'llm-judge',
          metricConfig: {},
        },
      });
      return (
        <FormProvider {...methods}>
          <MetricSelector workspace="default" />
        </FormProvider>
      );
    };

    render(<Wrapper />);

    // Verify required fields are marked via KUI's required class
    const requiredFields = screen
      .getAllByTestId('nv-form-field-root')
      .filter((el) => el.classList.contains('nv-form-field-root--required'));

    // Should have at least 3 required fields: Score Name, Minimum, Maximum
    expect(requiredFields.length).toBeGreaterThanOrEqual(3);
  });

  it('should show correct placeholder text for LLM judge fields', () => {
    const Wrapper = () => {
      const methods = useForm({
        defaultValues: {
          metricType: 'llm-judge',
          metricConfig: {},
        },
      });
      return (
        <FormProvider {...methods}>
          <MetricSelector workspace="default" />
        </FormProvider>
      );
    };

    render(<Wrapper />);

    // Verify placeholder text
    expect(screen.getByPlaceholderText('quality')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Overall quality of the response')).toBeInTheDocument();
  });
});
