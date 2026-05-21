// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { mergeURLSearchParams } from './search';

describe('search utils', () => {
  describe('mergeURLSearchParams', () => {
    it('correctly merges search params', () => {
      const a = new URLSearchParams({ param1: '1' });
      const b = { param2: '2' };

      const mergedURLSearchParams = mergeURLSearchParams(a, b);

      expect(Object.fromEntries(mergedURLSearchParams.entries())).toEqual({
        param1: '1',
        param2: '2',
      });
    });

    it('correctly uses the value from b when a property exists in both a and b', () => {
      const a = new URLSearchParams({ param1: '1', param2: '2' });
      const b = { param2: 'overwritten', param3: '3' };

      const mergedURLSearchParams = mergeURLSearchParams(a, b);

      expect(Object.fromEntries(mergedURLSearchParams.entries())).toEqual({
        param1: '1',
        param2: 'overwritten',
        param3: '3',
      });
    });

    it('correctly uses `undefined` values in b to delete from a', () => {
      const a = new URLSearchParams({ param1: '1', param2: '2' });
      const b = { param2: undefined, param3: '3' };

      const mergedURLSearchParams = mergeURLSearchParams(a, b);

      expect(Object.fromEntries(mergedURLSearchParams.entries())).toEqual({
        param1: '1',
        param3: '3',
      });
    });
  });
});
