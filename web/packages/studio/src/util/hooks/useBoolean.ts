// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useState } from 'react';

/**
 * A custom hook helper for boolean state variables that returns
 * callbacks that wrap setting the variable to true or false.
 * ex. const [isModalOpen, openModal, closeModal] = useBoolean();
 */
export const useBoolean = (defaultValue?: boolean): [boolean, () => void, () => void] => {
  const [isValid, setIsValid] = useState<boolean>(defaultValue ?? false);
  const setTrue = () => setIsValid(true);
  const setFalse = () => setIsValid(false);
  return [isValid, setTrue, setFalse];
};
