/*
 * SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
 */

import { flagDefinitions, FeatureFlags } from '@studio/constants/featureFlags/featureFlags';
import { parseFlags } from '@studio/constants/featureFlags/utils';

// --- Exports ---

/**
 * Parsed feature flags. Access flags as typed properties.
 *
 * @example
 * import { featureFlags } from '@studio/constants/featureFlags';
 *
 * if (featureFlags.experimentalChat) {
 *   // render experimental chat UI
 * }
 */
export const featureFlags = parseFlags<FeatureFlags>(flagDefinitions, import.meta.env);
