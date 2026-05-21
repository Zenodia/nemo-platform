# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


class ModelFormat(str, Enum):
    NIM = "nvidia-nim"
    OPENAI = "openai"


# Different metrics have different supported model types. "vlm" also exists as a supported type but not used.
class EvalFactoryModelType(str, Enum):
    CHAT = "chat"
    COMPLETIONS = "completions"
