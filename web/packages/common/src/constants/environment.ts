/*
 * SPDX-FileCopyrightText: Copyright (c) 2022-2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
 */

import { resolveBrowserBaseUrl } from '@nemo/sdk/src/utils/url';

/**
 * Use this function to get environment variables.
 * We use import.meta.env to get the environment variables, but replace at runtime to support dynamic k8s environment variables.
 * @param envVarKey - The key of the environment variable to get.
 * @returns The value of the environment variable, or undefined if the environment variable is not set.
 */
const getEnvVar = (envVarKey: string) => (import.meta.env[envVarKey] as string)?.toLowerCase();

export const PLATFORM_BASE_URL = resolveBrowserBaseUrl(getEnvVar('VITE_PLATFORM_BASE_URL'));
