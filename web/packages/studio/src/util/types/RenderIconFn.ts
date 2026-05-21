// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ReactNode, SVGProps } from 'react';

type RenderIconProps = Pick<SVGProps<SVGSVGElement>, 'width' | 'height'>;

/**
 * Just a little utility type for components that have a `renderIcon` prop.
 */
export type RenderIconFn = (props: RenderIconProps) => ReactNode;
