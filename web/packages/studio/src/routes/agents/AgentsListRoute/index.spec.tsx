// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ROUTES } from '@studio/constants/routes';
import { workspace1 } from '@studio/mocks/entity-store/projects';
import { AgentsListRoute } from '@studio/routes/agents/AgentsListRoute';
import { getAgentsListRoute } from '@studio/routes/utils';
import { renderRoute, screen } from '@studio/tests/util/render';

const workspace = workspace1.workspace;

const renderList = () =>
  renderRoute(<AgentsListRoute />, {
    history: getAgentsListRoute(workspace),
    routes: [{ path: ROUTES.workspace.agentsList, element: <AgentsListRoute /> }],
  });

describe('AgentsListRoute', () => {
  it('renders the page shell', async () => {
    renderList();
    expect(await screen.findByText('Agents')).toBeInTheDocument();
    expect(
      screen.getByText('View and manage AI agents and their deployments.')
    ).toBeInTheDocument();
  });
});
