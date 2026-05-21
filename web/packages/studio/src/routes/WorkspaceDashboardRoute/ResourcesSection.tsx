// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  Card,
  Divider,
  Flex,
  Grid,
  Stack,
  Text,
  VerticalNav,
  VerticalNavIcon,
  VerticalNavLink,
  VerticalNavText,
} from '@nvidia/foundations-react-core';
import { ReportTraceModal } from '@studio/components/ReportTraceModal';
import { TELEMETRY_ENABLED } from '@studio/constants/environment';
import { LINK_DOCS_SDK, LINK_DOCS_STUDIO, LINK_GITHUB_ISSUES } from '@studio/constants/links';
import { Book, Bug, ExternalLink, Route } from 'lucide-react';
import { FC, useState } from 'react';

export const ResourcesSection: FC = () => {
  const [isTraceModalOpen, setIsTraceModalOpen] = useState(false);

  const helpItems = [
    { id: 'report-bug', slotLabel: 'Report a Bug', href: LINK_GITHUB_ISSUES },
    ...(TELEMETRY_ENABLED ? [{ id: 'report-trace', slotLabel: 'Report a Trace' }] : []),
  ];

  return (
    <>
      <Card className="w-full">
        <Grid cols={{ sm: 1, md: 2 }} gap="density-5xl">
          {/* Getting Started Documentation */}
          <Stack gap="density-lg" className="min-w-0">
            <Text kind="label/bold/xl">Documentation</Text>
            <VerticalNav
              className="w-full bg-surface-raised border-0"
              items={[
                { id: 'studio-docs', slotLabel: 'Studio Documentation', href: LINK_DOCS_STUDIO },
                { id: 'sdk-docs', slotLabel: 'SDK Documentation', href: LINK_DOCS_SDK },
              ]}
              renderLink={(item) => (
                <>
                  <VerticalNavLink href={item.href} target="_blank" rel="noopener noreferrer">
                    <VerticalNavIcon>
                      <Book width={16} height={16} />
                    </VerticalNavIcon>
                    <VerticalNavText>{item.slotLabel}</VerticalNavText>
                    <Flex align="center" className="ml-auto">
                      <ExternalLink width={14} height={14} />
                    </Flex>
                  </VerticalNavLink>
                  {item.id === 'studio-docs' && <Divider />}
                </>
              )}
            />
          </Stack>

          {/* Help & Support */}
          {helpItems.length > 0 && (
            <Stack gap="density-lg" className="min-w-0">
              <Text kind="label/bold/xl">Help & Support</Text>
              <VerticalNav
                className="w-full bg-surface-raised border-0"
                items={helpItems}
                renderLink={(item) => {
                  if (item.id === 'report-bug') {
                    return (
                      <>
                        <VerticalNavLink href={item.href} target="_blank" rel="noopener noreferrer">
                          <VerticalNavIcon>
                            <Bug width={16} height={16} />
                          </VerticalNavIcon>
                          <VerticalNavText>{item.slotLabel}</VerticalNavText>
                          <Flex align="center" className="ml-auto">
                            <ExternalLink width={14} height={14} />
                          </Flex>
                        </VerticalNavLink>
                        {TELEMETRY_ENABLED && <Divider />}
                      </>
                    );
                  }
                  if (item.id === 'report-trace') {
                    return (
                      <VerticalNavLink
                        href="#"
                        onClick={(e) => {
                          e.preventDefault();
                          setIsTraceModalOpen(true);
                        }}
                      >
                        <VerticalNavIcon>
                          <Route width={16} height={16} />
                        </VerticalNavIcon>
                        <VerticalNavText>{item.slotLabel}</VerticalNavText>
                      </VerticalNavLink>
                    );
                  }
                  return null;
                }}
              />
            </Stack>
          )}
        </Grid>
      </Card>

      <ReportTraceModal open={isTraceModalOpen} onClose={() => setIsTraceModalOpen(false)} />
    </>
  );
};
