// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  VerticalNavAccordionContent,
  VerticalNavAccordionItem,
  VerticalNavAccordionRoot,
  VerticalNavAccordionTrigger,
  VerticalNavIcon,
  VerticalNavLink,
  VerticalNavListItem,
  VerticalNavSubLink,
  VerticalNavSubList,
  VerticalNavSubListItem,
  VerticalNavText,
  type VerticalNavItem,
  type VerticalNavSubItem,
} from '@nvidia/foundations-react-core';
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import type { FC } from 'react';
import { NavLink } from 'react-router-dom';

interface NavItemProps {
  item: VerticalNavItem;
  isActive: (href: string) => boolean;
  accordionOpen: boolean | undefined;
  onAccordionChange: (itemId: string, open: boolean) => void;
}

export const NavItem: FC<NavItemProps> = ({ item, isActive, accordionOpen, onAccordionChange }) => {
  const active = item.active ?? (item.href !== undefined ? isActive(item.href) : false);

  // Section header (no href, no subItems)
  if (item.href === undefined && !item.subItems?.length) {
    return (
      <VerticalNavListItem>
        <div className="flex items-center gap-2 px-4 py-2" aria-hidden>
          {item.slotIcon && <VerticalNavIcon>{item.slotIcon}</VerticalNavIcon>}
          <VerticalNavText {...item.attributes?.VerticalNavText}>{item.slotLabel}</VerticalNavText>
        </div>
      </VerticalNavListItem>
    );
  }

  // Accordion (has subItems)
  if (item.subItems?.length) {
    const isOpen =
      accordionOpen ?? (item.open !== undefined ? item.open : item.defaultOpen !== false);
    return (
      <VerticalNavListItem>
        <VerticalNavAccordionRoot
          defaultValue={item.defaultOpen !== false ? [item.id] : []}
          value={item.open !== undefined ? (item.open ? [item.id] : []) : undefined}
          onValueChange={(v) => {
            onAccordionChange(item.id, v.includes(item.id));
            item.onOpenChange?.(v.includes(item.id));
          }}
          {...item.attributes?.VerticalNavAccordionRoot}
        >
          <VerticalNavAccordionItem value={item.id} {...item.attributes?.VerticalNavAccordionItem}>
            <VerticalNavAccordionTrigger {...item.attributes?.VerticalNavAccordionTrigger}>
              {item.slotIcon && <VerticalNavIcon>{item.slotIcon}</VerticalNavIcon>}
              <VerticalNavText {...item.attributes?.VerticalNavText}>
                {item.slotLabel}
              </VerticalNavText>
              {isOpen ? <ChevronUp /> : <ChevronDown />}
            </VerticalNavAccordionTrigger>
            <VerticalNavAccordionContent {...item.attributes?.VerticalNavAccordionContent}>
              <VerticalNavSubList {...item.attributes?.VerticalNavSubList}>
                {item.subItems.map((sub) => (
                  <VerticalNavSubListItem
                    key={sub.id}
                    {...(sub as VerticalNavSubItem).attributes?.VerticalNavSubListItem}
                  >
                    <VerticalNavSubLink
                      active={sub.active ?? (sub.href ? isActive(sub.href) : false)}
                      disabled={!sub.href}
                      {...(sub as VerticalNavSubItem).attributes?.VerticalNavSubLink}
                      asChild
                    >
                      <NavLink to={sub.href ?? ''}>
                        {sub.slotIcon && <VerticalNavIcon>{sub.slotIcon}</VerticalNavIcon>}
                        <VerticalNavText
                          {...(sub as VerticalNavSubItem).attributes?.VerticalNavText}
                        >
                          {sub.slotLabel}
                        </VerticalNavText>
                      </NavLink>
                    </VerticalNavSubLink>
                  </VerticalNavSubListItem>
                ))}
              </VerticalNavSubList>
            </VerticalNavAccordionContent>
          </VerticalNavAccordionItem>
        </VerticalNavAccordionRoot>
      </VerticalNavListItem>
    );
  }

  // Link (href, no subItems)
  return (
    <VerticalNavListItem>
      <VerticalNavLink
        active={active}
        disabled={!item.href}
        {...item.attributes?.VerticalNavLink}
        className="py-3 px-4"
        asChild
      >
        <NavLink to={item.href ?? ''}>
          {item.slotIcon && <VerticalNavIcon>{item.slotIcon}</VerticalNavIcon>}
          <VerticalNavText {...item.attributes?.VerticalNavText}>{item.slotLabel}</VerticalNavText>
          {item.attributes?.VerticalNavLink?.target === '_blank' && <ExternalLink />}
        </NavLink>
      </VerticalNavLink>
    </VerticalNavListItem>
  );
};
