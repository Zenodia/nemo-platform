// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  Tooltip,
  VerticalNavIcon,
  VerticalNavLink,
  VerticalNavListItem,
  type VerticalNavItem,
} from '@nvidia/foundations-react-core';
import type { FC } from 'react';
import { NavLink } from 'react-router-dom';

interface CollapsedNavItemProps {
  item: VerticalNavItem;
  isActive: (href: string) => boolean;
}

export const CollapsedNavItem: FC<CollapsedNavItemProps> = ({ item, isActive }) => {
  const href = item.href ?? item.subItems?.[0]?.href;
  if (!href || !item.slotIcon) return null;
  const active = item.active ?? isActive(href);

  return (
    <VerticalNavListItem>
      <Tooltip slotContent={item.slotLabel} side="right">
        <VerticalNavLink
          active={active}
          disabled={!href}
          {...item.attributes?.VerticalNavLink}
          className="py-3 px-4"
          asChild
        >
          <NavLink to={href}>
            <VerticalNavIcon className="[&>svg]:text-primary">{item.slotIcon}</VerticalNavIcon>
          </NavLink>
        </VerticalNavLink>
      </Tooltip>
    </VerticalNavListItem>
  );
};
