// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Button, ButtonProps, Spinner } from '@nvidia/foundations-react-core';
import { FC } from 'react';

interface Props extends Omit<ButtonProps, 'size' | 'sx'> {
  showSpinner?: boolean;
}

export const PanelFooterButton: FC<Props> = (props) => {
  const { children, showSpinner, ...rest } = props;

  return (
    <Button className="flex flex-1 h-full" size="small" {...rest}>
      {showSpinner && rest.disabled ? '' : children}
      {showSpinner && <Spinner aria-label="Loading" size="small" className="w-4 h-4" />}
    </Button>
  );
};
