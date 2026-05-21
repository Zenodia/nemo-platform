// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { zodResolver } from '@hookform/resolvers/zod';
import { DEFAULT_WORKSPACE } from '@nemo/common/src/models/constants';
import { NewExportJobForm } from '@studio/components/form/NewExportJobForm';
import {
  getDefaultExportFileName,
  newExportJobFormSchema,
} from '@studio/components/form/NewExportJobForm/constants';
import { PLATFORM_BASE_URL } from '@studio/constants/environment';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { workspace1 } from '@studio/mocks/entity-store/projects';
import { server } from '@studio/mocks/node';
import { mockUseParams } from '@studio/tests/util/mockUseParams';
import { render } from '@studio/tests/util/render';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { FormProvider, useForm } from 'react-hook-form';
import { z } from 'zod';

// Mock brand assets icons
vi.mock('lucide-react', () => ({
  Database: () => <span data-testid="db-icon" />,
  Trash: () => <span data-testid="trash-icon" />,
  Filter: () => <span data-testid="filter-icon" />,
}));

const ENTRIES_URL = '*/apis/intake/v2/workspaces/:workspace/entries';

// Test wrapper component that provides form context
const FormWrapper = ({
  children,
  defaultValues,
}: {
  children: React.ReactNode;
  defaultValues?: Partial<z.infer<typeof newExportJobFormSchema>>;
}) => {
  const methods = useForm<z.infer<typeof newExportJobFormSchema>>({
    resolver: zodResolver(newExportJobFormSchema),
    defaultValues: {
      export_file_name: getDefaultExportFileName(),
      project: `${DEFAULT_WORKSPACE}/${workspace1.name}`,
      config: { limit: 1000 },
      ...defaultValues,
    },
  });

  return <FormProvider {...methods}>{children}</FormProvider>;
};

describe('NewExportJobForm', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    mockUseParams({
      [ROUTE_PARAMS.workspace]: DEFAULT_WORKSPACE,
    });
  });

  it('queries filesets with purpose filter set to dataset', async () => {
    const requestUrls: string[] = [];
    server.use(
      http.get(
        `${PLATFORM_BASE_URL}/apis/files/v2/workspaces/:workspace/filesets`,
        ({ request }) => {
          requestUrls.push(request.url);
          return HttpResponse.json({
            data: [],
            pagination: {
              page: 1,
              page_size: 25,
              current_page_size: 0,
              total_pages: 1,
              total_results: 0,
            },
          });
        }
      )
    );

    render(
      <FormWrapper>
        <NewExportJobForm />
      </FormWrapper>
    );

    await waitFor(() => {
      expect(requestUrls.length).toBeGreaterThan(0);
    });

    const url = new URL(requestUrls[0]);
    expect(url.searchParams.get('filter[purpose]')).toBe('dataset');
  });

  it('renders the form with key elements', async () => {
    render(
      <FormWrapper>
        <NewExportJobForm />
      </FormWrapper>
    );

    // Check for description text
    expect(
      await screen.findByText('Export entries to a Dataset for evaluation.')
    ).toBeInTheDocument();

    // Check for dataset destination select
    expect(screen.getByText('Dataset Destination')).toBeInTheDocument();

    // Check for export file name field
    expect(screen.getByText('Export File Name')).toBeInTheDocument();

    // Check for limit field
    expect(screen.getByText('Limit')).toBeInTheDocument();

    // Check for row transformation checkbox
    expect(screen.getByText('Row Transformation')).toBeInTheDocument();

    // Check for export criteria section
    expect(screen.getByText('Export Criteria')).toBeInTheDocument();
  });

  it('shows default message when no filters are applied', async () => {
    render(
      <FormWrapper>
        <NewExportJobForm />
      </FormWrapper>
    );

    expect(
      await screen.findByText('Add at least one filter to export records to a dataset.')
    ).toBeInTheDocument();
  });

  it('allows selecting a dataset from the dropdown', async () => {
    render(
      <FormWrapper>
        <NewExportJobForm />
      </FormWrapper>
    );

    // Find and click the dataset combobox
    const datasetSelect = await screen.findByRole('combobox', { name: 'Dataset Destination' });
    await user.click(datasetSelect);

    // Wait for and select the first dataset option
    const option = await screen.findByRole('option', { name: 'dataset-187625' });
    await user.click(option);

    // Verify dataset was selected (the db icon and name should be visible in the trigger)
    expect(screen.getByTestId('db-icon')).toBeInTheDocument();
  });

  it('shows Add Criteria dropdown with available filter options', async () => {
    render(
      <FormWrapper>
        <NewExportJobForm />
      </FormWrapper>
    );

    // Check that Add Criteria is present
    expect(await screen.findByText('Add Criteria')).toBeInTheDocument();

    // Find the select for adding criteria
    const addCriteriaSelect = await screen.findByRole('combobox', {
      name: /Add criteria/i,
    });
    expect(addCriteriaSelect).toBeInTheDocument();
  });

  it('adds a filter criterion when selected from dropdown', async () => {
    render(
      <FormWrapper>
        <NewExportJobForm />
      </FormWrapper>
    );

    // Click on the Add Criteria select
    const addCriteriaSelect = await screen.findByRole('combobox', {
      name: /Add criteria/i,
    });
    await user.click(addCriteriaSelect);

    // Select the "project" filter option
    const projectOption = await screen.findByRole('option', { name: 'project' });
    await user.click(projectOption);

    // Verify the filter was added (there should now be a "project" label)
    await waitFor(() => {
      expect(screen.getByText('project')).toBeVisible();
    });
  });

  it('removes a filter criterion when delete button is clicked', async () => {
    render(
      <FormWrapper defaultValues={{ config: { filters: { project: '' } } }}>
        <NewExportJobForm />
      </FormWrapper>
    );

    // Verify the project filter is displayed within form
    expect(await screen.findByText('project')).toBeVisible();

    // Click the trash button to remove the filter
    const deleteButton = await screen.findByTestId('trash-icon');
    expect(deleteButton).toBeInTheDocument();
    await user.click(deleteButton!);

    // Verify the filter was removed
    await waitFor(() => {
      expect(screen.queryByTestId('trash-icon')).not.toBeInTheDocument();
    });
  });

  it('displays matching record count when filters are applied', async () => {
    // Mock the entries list endpoint to return a count
    server.use(
      http.get(ENTRIES_URL, () =>
        HttpResponse.json({
          object: 'list',
          data: [],
          pagination: {
            page: 1,
            page_size: 1,
            current_page_size: 0,
            total_pages: 1,
            total_results: 42,
          },
        })
      )
    );

    render(
      <FormWrapper defaultValues={{ config: { filters: { project: 'test' } } }}>
        <NewExportJobForm />
      </FormWrapper>
    );

    // Wait for the record count to be displayed
    expect(
      await screen.findByText('42 records matching the filters will be exported')
    ).toBeInTheDocument();
  });

  it('shows error message when entries fetch fails', async () => {
    // Suppress expected console.error
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    server.use(
      http.get(ENTRIES_URL, () =>
        HttpResponse.json({ error: 'Internal Server Error' }, { status: 500 })
      )
    );

    render(
      <FormWrapper defaultValues={{ config: { filters: { project: 'test' } } }}>
        <NewExportJobForm />
      </FormWrapper>
    );

    // Wait for the error message
    expect(await screen.findByText(/Error fetching entries:/)).toBeInTheDocument();

    consoleSpy.mockRestore();
  });
});
