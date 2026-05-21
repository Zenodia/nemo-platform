// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { User } from 'oidc-client-ts';
import { useMemo } from 'react';
import { useAuth } from 'react-oidc-context';

export type AuthProfile = {
  name: string;
  email: string;
  workspace: string;
  state?: {
    path: string;
    search: string;
  };
};

const getWorkspace = (user: User) => {
  const email = user.profile.email ?? `${user.profile.unique_name}`;
  return email
    ? email.split('@')[0]
    : (user.profile.name?.replace(/\s+/g, '-').toLowerCase() ?? '');
};

export const getUserAuthProfile = (user: User): AuthProfile => ({
  name: user.profile.name ?? '',
  email: user.profile.email ?? `${user.profile.unique_name}`,
  workspace: getWorkspace(user),
  state: user.state as AuthProfile['state'],
});

export const useAuthProfile = (): AuthProfile | undefined => {
  const auth = useAuth();
  const user = auth?.user;

  return useMemo(() => {
    if (!user) return undefined;
    return getUserAuthProfile(user);
  }, [user]);
};
