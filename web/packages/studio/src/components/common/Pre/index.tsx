// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { FC, HTMLProps, PropsWithChildren, ReactNode } from 'react';

export const Pre: FC<
  PropsWithChildren<
    Omit<HTMLProps<HTMLDivElement>, 'slot'> & {
      className?: string;
      wrapper?: boolean;
      slot?: ReactNode;
    }
  >
> = ({ children, className, wrapper = false, slot, ...props }) => {
  const content = (
    <div className={`whitespace-pre-wrap font-mono${className ? ` ${className}` : ''}`} {...props}>
      {children}
    </div>
  );

  if (wrapper || slot) {
    return (
      <div className="relative w-full flex justify-between bg-surface-base" {...props}>
        {content}
        {slot}
      </div>
    );
  }

  return content;
};
