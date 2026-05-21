// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useToast } from '@nemo/common/src/providers/toast/useToast';
import {
  filesDeleteFileset,
  modelsDeleteAllDeploymentConfigVersions,
  modelsDeleteAllDeploymentVersions,
  modelsDeleteModel,
  modelsGetLatestDeployment,
  modelsGetLatestDeploymentConfig,
} from '@nemo/sdk/generated/platform/api';
import { ModelDeploymentStatus, type ModelDeployment } from '@nemo/sdk/generated/platform/schema';
import { useDeleteDeploymentAndConfig } from '@studio/routes/DeploymentsListRoute/useDeleteDeploymentAndConfig';
import { wrapper } from '@studio/tests/util/TestQueryClient';
import { act, renderHook } from '@testing-library/react';

vi.mock('@nemo/common/src/providers/toast/useToast');
vi.mock('@nemo/sdk/generated/platform/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@nemo/sdk/generated/platform/api')>();
  return {
    ...actual,
    filesDeleteFileset: vi.fn(),
    modelsDeleteAllDeploymentConfigVersions: vi.fn(),
    modelsDeleteAllDeploymentVersions: vi.fn(),
    modelsDeleteModel: vi.fn(),
    modelsGetLatestDeployment: vi.fn(),
    modelsGetLatestDeploymentConfig: vi.fn(),
  };
});

const mockUseToast = vi.mocked(useToast);
const mockFilesDeleteFileset = vi.mocked(filesDeleteFileset);
const mockModelsDeleteAllDeploymentConfigVersions = vi.mocked(
  modelsDeleteAllDeploymentConfigVersions
);
const mockModelsDeleteAllDeploymentVersions = vi.mocked(modelsDeleteAllDeploymentVersions);
const mockModelsDeleteModel = vi.mocked(modelsDeleteModel);
const mockModelsGetLatestDeployment = vi.mocked(modelsGetLatestDeployment);
const mockModelsGetLatestDeploymentConfig = vi.mocked(modelsGetLatestDeploymentConfig);

const workspace = 'workspace';
const deployment: ModelDeployment = {
  name: 'deployment',
  workspace,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  entity_version: 1,
  config: 'deployment-config',
  config_version: 1,
  status: ModelDeploymentStatus.READY,
};

describe('useDeleteDeploymentAndConfig', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();

    mockUseToast.mockReturnValue({
      success: vi.fn(),
      error: vi.fn(),
      info: vi.fn(),
      warning: vi.fn(),
      workingWithId: vi.fn(),
      dismissToast: vi.fn(),
    } as unknown as ReturnType<typeof useToast>);

    mockFilesDeleteFileset.mockResolvedValue(undefined as never);
    mockModelsDeleteAllDeploymentConfigVersions.mockResolvedValue(undefined as never);
    mockModelsDeleteAllDeploymentVersions.mockResolvedValue(undefined as never);
    mockModelsDeleteModel.mockResolvedValue(undefined as never);
    mockModelsGetLatestDeploymentConfig.mockResolvedValue({ nim_deployment: {} } as never);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('resolves once the deployment reaches DELETING and cleans up config after DELETED', async () => {
    mockModelsGetLatestDeployment
      .mockResolvedValueOnce({
        ...deployment,
        status: ModelDeploymentStatus.DELETING,
      })
      .mockResolvedValueOnce({
        ...deployment,
        status: ModelDeploymentStatus.DELETING,
      })
      .mockResolvedValueOnce({
        ...deployment,
        status: ModelDeploymentStatus.DELETED,
      });

    const { result } = renderHook(() => useDeleteDeploymentAndConfig(workspace), { wrapper });

    await act(async () => {
      await result.current.deleteDeploymentAndConfig(deployment);
    });

    expect(mockModelsDeleteAllDeploymentVersions).toHaveBeenCalledWith(workspace, deployment.name);
    expect(mockModelsDeleteAllDeploymentConfigVersions).not.toHaveBeenCalled();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(2000);
    });

    expect(mockModelsDeleteAllDeploymentConfigVersions).toHaveBeenCalledWith(
      workspace,
      deployment.config
    );
  });
});
